"""
usage: python svmlitegen.py
"""
from __future__ import division
import csv
import datetime
import database
import numpy as np
import re
import sys


LDA_TOPICS_FNAME = "debates.doc.topics"
DEBATE_DATA_FNAME = "oct3.labeled"


COUNT_QUERY = 'SELECT Count(*) FROM reactions,users WHERE reactions.userid=users.userid AND reactions.reaction="%s" %s AND reactions.time BETWEEN "%s" AND "%s"'
COUNT_QUERY_ALL = 'SELECT Count(*) FROM reactions,users WHERE reactions.userid=users.userid %s AND reactions.time BETWEEN "%s" AND "%s"'
BARE_COUNT_QUERY = 'SELECT Count(*) FROM reactions,users WHERE reactions.userid=users.userid AND reactions.time BETWEEN "%s" AND "%s"'


def strptime(x, y):
    return datetime.datetime.strptime(x, y)


def svmlite_lines(react_type, user_attrs, label_fn, times, feats_list):
    if user_attrs:
        sql_attrs = ' AND ' + ' AND '.join(['users.%s="%s"' % x
                                  for x in user_attrs])
    else:
        sql_attrs = ''
    for (start, end), feats in zip(times, feats_list):
        if react_type == "all":
            query = COUNT_QUERY_ALL % (sql_attrs, start, end)
        else:
            query = COUNT_QUERY % (react_type, sql_attrs, start, end)
        num_reacts = database.fetch(query)[0][0]
        feat_str = ' '.join(["%s:%s" % (idx, feat) for idx, feat in feats
            + [('100', str((strptime(end, '%H:%M:%S') - strptime(start, '%H:%M:%S')).seconds))]])
        yield "%s %s\n" % (label_fn(num_reacts), feat_str)


def svmlite_lines_wlabels(labels, times, feats_list):
    #for (start, end), feats in zip(times, feats_list):
    for label, feats in zip(labels, feats_list):
        #len_feat = ' 100:%d' % ((strptime(end, '%H:%M:%S') - strptime(start, '%H:%M:%S')).seconds)
        len_feat = ''
        feat_str = ' '.join(["%s:%s" % (idx, feat) for idx, feat in feats]) + len_feat
        yield "%s %s\n" % (label, feat_str)


def counts_per_turn(react_type, user_attrs, per_second=True, curr_speaker=True):
    speakers = {'0': 'Moderator', '1': 'Romney', '2': 'Obama'}
    if user_attrs:
        user_attr_sql = ' AND ' + ' AND '.join(['users.%s="%s"' % x
                                  for x in user_attrs])
    else:
        user_attr_sql = ''
    with open(DEBATE_DATA_FNAME) as debate_data:
        reader = csv.reader(debate_data, delimiter=',', quotechar='"')
        react_counts = []
        for row in reader:
            query = BARE_COUNT_QUERY % (row[2], row[3])
            query += user_attr_sql
            if curr_speaker:
                print row
                query += ' AND reactions.reaction="%s:%s"' % (speakers[row[1]], react_type)
            react_count = database.fetch(query)[0][0]
            react_counts.append(react_count)
        return react_counts


def task_1(party):
    with open('task1%s.train' % (party), 'w') as f:
        attrs = [('candidate', party)]
        counts = counts_per_turn(None, attrs, curr_speaker=False)
        median = np.median(counts)
        labels = [1 if x > median else 0 for x in counts]
        feats = lda_topic_feats()
        for line in svmlite_lines_wlabels(labels, None, feats):
            f.write(line + '\n')


def task_2(party):
    with open('task2%s.train' % (party), 'w') as f:
        attrs = [('candidate', party)]
        agree_counts = counts_per_turn('Agree', attrs, per_second=False)
        disagree_counts = counts_per_turn('Disagree', attrs, per_second=False)
        ratios = [x / (y + 1) for x, y in zip(agree_counts, disagree_counts)]
        median = np.median(ratios)
        labels = [1 if x > median else 0 for x in ratios]
        feats = lda_topic_feats()
        for line in svmlite_lines_wlabels(labels, None, feats):
            f.write(line + '\n')


def task_3(party):
    with open('task3%s.train' % (party), 'w') as f:
        attrs = [('candidate', party)]
        spin_counts = counts_per_turn('Spin', attrs)
        dodge_counts = counts_per_turn('Dodge', attrs)
        totals = [x + y for x, y in zip(spin_counts, dodge_counts)]
        median = np.median(totals)
        labels = [1 if x > median else 0 for x in totals]
        feats = lda_topic_feats()
        for line in svmlite_lines_wlabels(labels, None, feats):
            f.write(line + '\n')


def binned_labels(react_type, user_attrs, times):
    if user_attrs:
        sql_attrs = ' AND ' + ' AND '.join(['users.%s="%s"' % x
                                  for x in user_attrs])
    else:
        sql_attrs = ''
    react_counts = []
    for start, end in times:
        if react_type == "all":
            query = COUNT_QUERY_ALL % (sql_attrs, start, end)
        else:
            query = COUNT_QUERY % (react_type.split(":")[0] + ":Agree",
                               sql_attrs, start, end)
        #print query
        st = strptime(start, '%H:%M:%S')
        nd = strptime(end, '%H:%M:%S')
        turn_time = (nd - st).seconds + 1
        num_reacts = database.fetch(query)[0][0]
        #print num_reacts
        react_counts.append(num_reacts / turn_time)
    median = np.median(react_counts)
    return [1 if x > median else 0 for x in react_counts]


def ratio_labels(react_type, user_attrs, times):
    if user_attrs:
        sql_attrs = ' AND ' + ' AND '.join(['users.%s="%s"' % x
                                  for x in user_attrs])
    else:
        sql_attrs = ''
    ratios = []
    for start, end in times:
        query = COUNT_QUERY % (react_type.split(":")[0] + ":Agree",
                               sql_attrs, start, end)
        num_agrees = database.fetch(query)[0][0]
        query = COUNT_QUERY % (react_type.split(":")[0] + ":Disagree",
                               sql_attrs, start, end)
        num_disagrees = database.fetch(query)[0][0]
        if num_disagrees == 0:
            ratios.append(num_agrees)
        else:
            ratios.append(num_agrees / num_disagrees)
    median = np.median(ratios)
    return [1 if x > median else 0 for x in ratios]


def identity_label(count):
    return count


def binned_label(count):
    ranges = [(0, 5), (5, 100), (100, 500), (500, float("inf"))]
    for idx, bounds in enumerate(ranges):
        if count >= bounds[0] and count < bounds[1]:
            return idx


def lda_topic_feats():
    with open(LDA_TOPICS_FNAME) as topics_file:
        for line_num, line in enumerate(topics_file):
            if line_num >= 197:
                break
            topics = re.findall(r'(\d+)\s+(\d\.\d+(E\-\d+)?)', line)
            topics.sort(key=lambda(x): int(x[0]))
            yield [tup[0:2] for tup in topics]


def turn_times():
    with open(DEBATE_DATA_FNAME) as debate_file:
        reader = csv.reader(debate_file, delimiter=',', quotechar='"')
        for row in reader:
            start = row[2]
            end = row[3]
            yield (start, end)


def svmgen_test():
    react_type = "Obama:Agree"
    user_attrs = {"gender": "female", "preferred_candidate": "obama"}.items()
    lines = svmlite_lines(react_type, user_attrs, binned_label, turn_times(),
                          lda_topic_feats())
    with open('test.train', 'w') as train:
        for line in lines:
            train.write(line)


def main(argv):
    task_1('obama')
    task_1('romney')
    task_2('obama')
    task_2('romney')
    task_3('obama')
    task_3('romney')


if __name__ == "__main__":
    main(sys.argv[1:])

