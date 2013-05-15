# Isaac Julien
# Get labeled topic information

import csv
import pylab
import numpy as np
from datetime import datetime
from time import strptime

# Get labeled topic percentages for each turn, along with start and end times of each turn:
def read_data(filename, topics):
    file = open(filename, 'r')
    file.readline() # First line is field names.
    SPEAKER_IDX = 2
    TOPIC_IDX = 5
    START_IDX = 0
    STOP_IDX = 1
    current_speaker = None
    start_time = None
    stop_time = None
    num_topics = len(topics)
    # Last feature is majority topic
    features = np.zeros(num_topics)
    turn_features = [] # features for each turn
    turn_info = [] # (start time, end time) for each turn
    contents = csv.reader(file, delimiter=',', quotechar='"')
    speaker = None
    for n, row in enumerate(contents):

        speaker = row[SPEAKER_IDX]

        if len(speaker) < 1:
            continue

        topic = row[TOPIC_IDX]

        #if topic == '9':
        #    continue

        if current_speaker is None:
            current_speaker = speaker
            time = row[START_IDX].split(".")[0] # Strip ms
            start_time = datetime(*strptime(time, "%H:%M:%S")[0:6])
        if speaker != current_speaker:
            current_speaker = speaker

            # Calculate feature percentages:
            fsum = 0.0
            for f in features:
                fsum += f
            for i in range(len(features)):
                features[i] /= fsum


            # TODO - THIS IS TEMPORARY:
            for i in range(len(features)):
                features[i] *= 1



            # Save information
            turn_features.append(features)
            turn_info.append((start_time, stop_time, speaker))
            # Reset start time:
            time = row[START_IDX].split(".")[0] # Strip ms
            start_time = datetime(*strptime(time, "%H:%M:%S")[0:6])
            features = np.zeros(num_topics)
            topic_index = topics.index(topic)
            features[topic_index] += float(1)
        time = row[STOP_IDX].split(".")[0] # Strip ms
        stop_time = datetime(*strptime(time, "%H:%M:%S")[0:6])
        topic_index = topics.index(topic)
        features[topic_index] += float(1)
    # Append final info:
    turn_features.append(features)
    turn_info.append((start_time, stop_time, speaker))
    return turn_features, turn_info



# Topic information:
def topic_info(filename):
    file = open(filename, 'r')
    file.readline()
    TOPIC_IDX = 5
    topics = {}
    contents = csv.reader(file, delimiter=',', quotechar='"')
    for n, row in enumerate(contents):
        topic = row[TOPIC_IDX]
        if topic not in topics.keys():
            topics[topic] = 1
        else:
            topics[topic] += 1
    return topics.keys()


# Return list of (reactions, times):
def rxns(rfile):
    file = open(rfile, 'r')
    file.readline()
    TIME_IDX = 2
    user_data = []
    contents = csv.reader(file, delimiter=',', quotechar='"')

    num_skipped = 0
    total = 0

    for n, row in enumerate(contents):
        time = row[TIME_IDX]
        time = time.split(".")[0] # Strip ms
        time = time.split(" ")[1] # Strip date
        time = datetime(*strptime(time, "%H:%M:%S")[0:6])

        REACTION = row[1]
        QUESTIONS = row[4:13]
        GENDER = 1 if row[14] == "male" else 0


        PARTY = 0
        if len(row[32]) > 0:
            PARTY = 1 if row[32][-1] == 'y' else 2
        MORE = row[26:29]

        RELIGION = 0
        rel = row[17].split(" ")[0]
        if rel == "christian":
            RELIGION = 1
        elif rel == "jewish":
            RELIGION = 2
        elif rel == "none":
            RELIGION = 3
        elif rel == "muslim":
            RELIGION = 4

        features = [GENDER, PARTY, RELIGION] + QUESTIONS + MORE

        skip = False
        for feature in features:
            if len(str(feature).strip()) < 1:
                num_skipped += 1
                skip = True
                break

        if skip:
            continue

        total += 1


        user_data.append((features, REACTION, time))

    print "Skipped " + str(num_skipped) + " data points with missing information."
    print "Got " + str(total) + " useable data points."
    return user_data


# Return features for turn associated with reaction time:
def get_topic_features(reaction_time, turn_info, turn_features):
    for i, turn in enumerate(turn_info):
        start_time = turn[0]
        stop_time = turn[1]
        if start_time < reaction_time < stop_time:
            return turn_features[i]
    return None


def get_lda_topic_features(reaction_time, turn_info, lda_features):
    for i, turn in enumerate(turn_info):
        start_time = turn[0]
        stop_time = turn[1]
        if start_time < reaction_time < stop_time:
            return lda_features[i]
    return None


def main():

    # Number of points to use for classification:
    num_points = 10000

    rfile = 'resources/data/reactions_oct3_4project.csv'

    user_data = rxns(rfile)

    path = "resources/corpora/"
    filename = path + "oct3_coded_transcript_sync.csv"
    topics = topic_info(filename)
    turn_features, turn_info = read_data(filename, topics)

    # USER DATA: [(features, REACTION, time)]
    # TURN INFO: [(start_time, stop_time, speaker)]
    # TURN FEATURES: [features]


    # Get LDA topic features:
    lda_features = []
    lda = open("lda_topics.txt", 'r')
    for line in lda:
        feature_vector = line.split()
        for i in range(len(feature_vector)):
            feature_vector[i] = feature_vector[i].split(":")[1]
        lda_features.append(feature_vector)



    features = []
    labels = []

    for data in user_data[:num_points]:
        user_features = data[0]
        REACTION = data[1].lower()
        time = data[2]


        # TODO - this is where you control whether you get LDA or Boydstun topic features:

        # LDA:
        #topic_features = get_lda_topic_features(time, turn_info, lda_features)

        # Boydstun:
        topic_features = get_topic_features(time, turn_info, turn_features)

        if topic_features is None:
            continue



        all_features = user_features + topic_features.tolist()


        reaction_map_all = {"obama:agree":0, "obama:disagree":1, "romney:agree":2, "romney:disagree":3,
                        "moderator:agree":4, "moderator:disagree":5, "obama:spin":6, "obama:dodge":7,
                        "romney:spin":8, "romney:dodge":9, "moderator:spin":10, "moderator:dodge":11}


        reaction_map_negative_or_positive = {"obama:agree":1, "obama:disagree":0, "romney:agree":1, "romney:disagree":0,
                        "moderator:agree":1, "moderator:disagree":0, "obama:spin":2, "obama:dodge":2,
                        "romney:spin":2, "romney:dodge":2, "moderator:spin":2, "moderator:dodge":2}


        # Write out label and features
        label = str(reaction_map_all[REACTION])

        features.append(all_features)
        labels.append(label)



    # Normalize features:
    num_features = len(features[0])
    maxes = np.zeros(num_features)
    for j in range(num_features):
        for i in range(len(features)):
            if maxes[j] < float(features[i][j]):
                maxes[j] = float(features[i][j])
    for i in range(len(features)):
        for j in range(num_features):
            if maxes[j] > 0:
                new_val = float(features[i][j]) / maxes[j]
                features[i][j] = str(new_val)



    # Write features and labels to file:
    out = open("topicinfo.csv", 'w')
    for i in range(len(features)):
        feature_vector = features[i]
        label = labels[i]
        line = label + "\t"
        for i in range(len(feature_vector)):
            line += str(i) + ":" + str(feature_vector[i]) + "\t"
        line += '\n'
        out.write(line)
    out.close()



if __name__ == "__main__":
    main()