from __future__ import print_function

from collections import Counter
import csv
import datetime
import json
import os
import re
import string
import sys


class DebateDoc:

    def __init__(self, speaker, id, text, **kargs):
        self.speaker = speaker
        self.id = id
        self.text = text
        for k, v in kargs.iteritems():
            setattr(self, "_%s" % (k), v)

    def name(self):
        return str(self.id)

    def start_time(self):
        try:
            hms = [int(n) for n in self._start_time.split(':')]
            return datetime.time(*hms)
        except AttributeError:
            return None

    def end_time(self):
        try:
            hms = [int(n) for n in self._stop_time.split(':')]
            return datetime.time(*hms)
        except AttributeError:
            return None

    def qtopic(self):
        return self._qtopic[0]

    def topic(self):
        return Counter(self._topic).most_common()[0][0]

    def frame(self):
        return Counter(self._frame).most_common()[0][0]

    def tone(self):
        return Counter(self._tone).most_common()[0][0]

    def __str__(self):
        return "%d,%s,%s,%s,%s,%s,%s,%s" % (self.id, self.speaker,
                                            self.start_time(), self.end_time(),
                                            self.qtopic(), self.topic(),
                                            self.frame(), self.tone())


class DebateDocSet:

    def __init__(self):
        self._train = []
        self._test = []
        self._next_id = 0

    def add_docs(self, corpus_info):
        corpus_fname = corpus_info['fname']
        speaker_field = corpus_info['speaker_field']
        text_field = corpus_info['text_field']
        with open(corpus_fname) as f:
            csvreader = csv.reader(f, delimiter=',', quotechar='"')
            for n, row in enumerate(csvreader):
                speaker = row[speaker_field]
                text = row[text_field].strip()
                # Corner cases
                if n == 0:
                    continue
                if n == 1:
                    last_speaker = speaker
                    turn = self._new_turn(text)
                    turn_data = self._new_turn_data(corpus_info, row)
                    continue
                # Normal cases
                if speaker != last_speaker:
                    self._add_doc(last_speaker, turn, turn_data,
                                  corpus_info['test_corpus'])
                    last_speaker = speaker
                    turn = self._new_turn(text)
                    turn_data = self._new_turn_data(corpus_info, row)
                else:
                    text = text.translate(string.maketrans("", ""), '"')
                    turn.append("%s" % (text))
                    self._add_to_turn_data(corpus_info, row, turn_data)
            self._add_doc(last_speaker, turn, turn_data,
                          corpus_info['test_corpus'])

    def _add_doc(self, speaker, turn, misc_data, test_corpus):
        turn_text = ' '.join(turn).lower()
        doc = DebateDoc(speaker, self._next_id, turn_text, **misc_data)
        if test_corpus:
            self._test.append(doc)
        else:
            self._train.append(doc)
        self._next_id += 1

    def _new_turn(self, text):
        # Turns in the presidential debate corpus start with NAME:
        # This removes those names.
        if re.match(r'^\w+:.*', text):
            return [text.split(':')[1].strip()]
        return [text]

    def _new_turn_data(self, corpus_info, line):
        turn_data = {}
        if 'time' in corpus_info:
            turn_data['start_time'] = line[corpus_info['time']['start']]
            turn_data['stop_time'] = line[corpus_info['time']['stop']]
        for field_type, field_index in corpus_info['misc'].iteritems():
            turn_data[str(field_type)] = [line[field_index]]
        return turn_data

    def _add_to_turn_data(self, corpus_info, line, turn_data):
        if 'time' in corpus_info:
            turn_data['stop_time'] = line[corpus_info['time']['stop']]
        for field_type, field_index in corpus_info['misc'].iteritems():
            turn_data[str(field_type)].append(line[field_index])

    def dump_malletdir(self, dirname):
        try:
            os.mkdir(dirname)
        except OSError:
            decision = raw_input('%s/ exists, continue anyway? (y,n): '
                                 % (dirname))
            if decision != 'y':
                sys.exit(1)
        for doc in self._train + self._test:
            with open(os.path.join(dirname, doc.name()), 'w') as f:
                f.write(doc.text)

    def dump_doc_data(self, fname):
        with open("%s.train" % (fname), 'w') as f:
            for doc in self._train:
                print(doc, file=f)
        with open("%s.test" % (fname), 'w') as f:
            for doc in self._test:
                print(doc, file=f)

    def complete_dump(self, name):
        self.dump_malletdir(name)
        self.dump_doc_data(name)


def main(argv):
    if len(argv) < 2:
        print("USAGE: python format.py output_name corpus_info_file")
    ds = DebateDocSet()
    outdir = argv[0]
    argv = argv[1:]
    input_file = argv[0]
    argv = argv[1:]
    with open(input_file) as f:
        corpora = json.loads(f.read())
        for corpus_info in corpora:
            ds.add_docs(corpus_info)
    ds.complete_dump(outdir)


if __name__ == "__main__":
    main(sys.argv[1:])
