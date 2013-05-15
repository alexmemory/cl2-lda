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
    features = np.zeros(num_topics + 1)
    turn_features = [] # features for each turn
    turn_info = [] # (start time, end time) for each turn
    contents = csv.reader(file, delimiter=',', quotechar='"')
    speaker = None
    for n, row in enumerate(contents):

        speaker = row[SPEAKER_IDX]

        if len(speaker) < 1:
            continue

        topic = row[TOPIC_IDX]

        if topic == '9':
            continue


        if current_speaker is None:
            current_speaker = speaker
            time = row[START_IDX].split(".")[0] # Strip ms
            start_time = datetime(*strptime(time, "%H:%M:%S")[0:6])
        if speaker != current_speaker:
            current_speaker = speaker
            # Calculate feature percentages:
            fsum = 0.0
            max = -1
            max_feature = None
            for f in features:
                fsum += f
            for i in range(len(features)):
                if features[i] > max:
                    max = features[i]
                    max_feature = i
                features[i] /= fsum
            # Calculate and save majority topic:
            majority_topic = topics[max_feature]
            features[-1] = majority_topic
            # Save information
            turn_features.append(features)
            turn_info.append((start_time, stop_time, speaker))
            # Reset start time:
            time = row[START_IDX].split(".")[0] # Strip ms
            start_time = datetime(*strptime(time, "%H:%M:%S")[0:6])
            features = np.zeros(num_topics + 1)
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


    '''
    counts = []
    for k in topics.keys():
        counts.append(topics[k])
    counts = sorted(counts)
    counts.reverse()
    pylab.scatter(range(len(counts)), counts)
    pylab.ylabel("Frequency")
    pylab.xlabel("Topic")
    pylab.xlim([-1, 25])
    pylab.ylim([-10, 500])
    pylab.title("Topic Frequency")
    pylab.show()
    '''


# Return list of (reactions, times):
def rxns(rfile):
    file = open(rfile, 'r')
    file.readline()
    TIME_IDX = 2
    RXN_IDX = 1
    VOTE_INDEX = 25 # who the user would vote for if he or she had to vote before the debate
    reactions_Obama = []
    reactions_Romney = []
    contents = csv.reader(file, delimiter=',', quotechar='"')
    for n, row in enumerate(contents):
        time = row[TIME_IDX]
        time = time.split(".")[0] # Strip ms
        time = time.split(" ")[1] # Strip date
        time = datetime(*strptime(time, "%H:%M:%S")[0:6])
        reaction = row[RXN_IDX]

        would_vote_for = row[VOTE_INDEX]
        if would_vote_for == "obama":
            reactions_Obama.append((reaction, time))
        elif would_vote_for == "romney":
            reactions_Romney.append((reaction, time))
    return reactions_Obama, reactions_Romney




def plot_reaction_counts(counts):
    counts = sorted(counts)
    counts.reverse()
    pylab.scatter(range(0,len(counts)), counts)
    pylab.axis([-10, len(counts)+10, min(counts)-100, max(counts)+1000])
    pylab.xlabel('Turn')
    pylab.ylabel('Number of Reactions')
    pylab.title('Number of Reactions per Turn')
    pylab.show()






# LABELING METHODS #####################################################################################################

def reaction_rates(turn_times, reactions):
    counts = []
    for i in range(len(turn_times)):
        count = 0
        start = turn_times[i][0]
        stop = turn_times[i][1]
        for j in range(len(reactions)):
            reaction_time = reactions[j][1]
            if stop > reaction_time > start:
                count += 1

        # Reaction rate:
        total_time = stop - start
        total_time = total_time.total_seconds()
        count /= total_time + 1.0

        counts.append(count)
    return counts

# Label = low (0) / medium (1) / high (2) number of reactions:
def LABEL_by_count(times, reactions):
    counts = reaction_rates(times, reactions)
    mean = np.median(counts)

    labels = []
    for i in range(len(counts)):
        count = counts[i]
        if count < mean:
            labels.append(0)
        else:
            labels.append(1)
    return labels


# Label = majority agree with current speaker (1), majority disagree (-1), neutral (0)
def LABEL_by_agreement(times, reactions):

    labels = []

    speaker_map = {'0':"moderator", '1':"romney", '2':"obama"}

    for i in range(len(times)):
        start = times[i][0]
        stop = times[i][1]

        speaker = speaker_map[times[i][2]]

        count_for = 0
        count_against = 0

        for j in range(len(reactions)):
            reaction_time = reactions[j][1]
            if stop > reaction_time > start:

                reaction = reactions[j][0].split(":")
                target = reaction[0].lower()
                value = reaction[1].lower()

                if speaker == target:
                    if value == "agree":
                        count_for += 1
                    elif value == "disagree":
                        count_against += 1

        #print count_for, count_against

        if count_for > count_against:
            labels.append(1)
        elif count_against > count_for:
            labels.append(-1)
        else:
            labels.append(0)

    print labels
    return labels



# Label =
def LABEL_by_spin_dodge(times, reactions):

    counts = []
    labels = []

    speaker_map = {'0':"moderator", '1':"romney", '2':"obama"}

    for i in range(len(times)):
        start = times[i][0]
        stop = times[i][1]

        speaker = speaker_map[times[i][2]]

        spin_dodge = 0

        for j in range(len(reactions)):
            reaction_time = reactions[j][1]
            if stop > reaction_time > start:

                reaction = reactions[j][0].split(":")
                target = reaction[0].lower()
                value = reaction[1].lower()

                if speaker == target:
                    if value == "dodge" or value == "spin":
                        spin_dodge += 1

        # Reaction rate:
        total_time = stop - start
        total_time = total_time.total_seconds()
        spin_dodge /= total_time + 1.0
        counts.append(spin_dodge)

    mean = np.mean(counts)
    for i in range(len(counts)):
        count = counts[i]
        if count > mean:
            labels.append(1)
        else: labels.append(0)

    #print counts
    #print labels
    return labels



####### TODO Get more features ################


#todo - combine user info with topic info as features
def FEATURES_user_questions():
    pass


def FEATURES_all(turn_info, reactions):

    for j in range(len(reactions)):
        reaction_time = reactions[j][1]



# Label = majority reaction (ex, "Romney:disagree")
def LABEL_by_everything(times, reactions):
    pass # TODO - not enough data for this one

########################################################################################################################








def main():


    rfile = 'resources/data/reactions_oct3_4project.csv'
    reactions_Obama, reactions_Romney = rxns(rfile)


    path = "resources/corpora/"
    filename = path + "oct3_coded_transcript_sync.csv"

    topics = topic_info(filename)
    turn_features, turn_info = read_data(filename, topics)

    #plot_reaction_counts(counts)


    # TODO : SET TO EITHER reactions_Obama OR reactions_Romney:
    labels = LABEL_by_spin_dodge(turn_info, reactions_Romney)



    # Write features to file:
    out = open("topicinfo.csv", 'w')
    for i in range(len(turn_features)):
        out.write(str(labels[i]) + "\t")
        features = turn_features[i]
        for j in range(len(features)-1):
            # Use topic ID as feature name:
            out.write(str(topics[j]) + ":" + str(features[j]) + "\t")
        #out.write(str("majority") + ":" + '"' + str(features[-1]) + '"')
        out.write('\n')

    out.close()



if __name__ == "__main__":
    main()