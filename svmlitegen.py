"""
usage: python svmlitegen.py <reaction type> <binned|ratio|identity> <user attributes (e.g., "party=democrat")
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


def strptime(x, y):
    return datetime.datetime.strptime(x, y)


def svmlite_lines(react_type, user_attrs, label_fn, times, feats_list):
    if user_attrs:
        sql_attrs = ' AND ' + ' AND '.join(['users.%s="%s"' % x
                                  for x in user_attrs])
    else:
        sql_attrs = ''
    for (start, end), feats in zip(times, feats_list):
        query = COUNT_QUERY % (react_type, sql_attrs, start, end)
        num_reacts = database.fetch(query)[0][0]
        feat_str = ' '.join(["%s:%s" % (idx, feat) for idx, feat in feats
            + [('100', str((strptime(end, '%H:%M:%S') - strptime(start, '%H:%M:%S')).seconds))]])
        yield "%s %s\n" % (label_fn(num_reacts), feat_str)


def svmlite_lines_wlabels(labels, times, feats_list):
    #for (start, end), feats in zip(times, feats_list):
    for (start, end), label, feats in zip(times, labels, feats_list):
        feat_str = ' '.join(["%s:%s" % (idx, feat) for idx, feat in feats
            + [('100', str((strptime(end, '%H:%M:%S') - strptime(start, '%H:%M:%S')).seconds))]])
        yield "%s %s\n" % (label, feat_str)


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
    if len(argv) < 2:
        print "Not enough args"
        sys.exit(1)
    react_type = argv[0]
    label_type = argv[1]
    user_attrs = [tuple(x.split('=')) for x in argv[2:]]
    if label_type == 'binned':
        label_fn = binned_label
    elif label_type == 'identity':
        label_fn = identity_label
    elif label_type == 'ratio':
        times = list(turn_times())
        labels = ratio_labels(react_type, user_attrs, times)
        with open('ratio.train', 'w') as train:
            for line in svmlite_lines_wlabels(labels, times, lda_topic_feats()):
                train.write(line)
        sys.exit(0)
    lines = svmlite_lines(react_type, user_attrs, label_fn, turn_times(),
                          lda_topic_feats())
    file_name = '_'.join(argv)
    lines = list(lines)
    split = int(len(lines))
    with open(file_name + ".train", 'w') as train:
        for line_num in range(split):
            train.write(lines[line_num])
    with open(file_name + ".test", 'w') as test:
        for line_num in range(split, len(lines)):
            test.write(lines[line_num])


if __name__ == "__main__":
    main(sys.argv[1:])
