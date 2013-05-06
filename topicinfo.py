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
    output = [] # features for each turn
    times = [] # (start time, end time) for each turn
    contents = csv.reader(file, delimiter=',', quotechar='"')
    for n, row in enumerate(contents):
        speaker = row[SPEAKER_IDX]
        topic = row[TOPIC_IDX]
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
            output.append(features)
            times.append((start_time, stop_time))
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
    output.append(features)
    times.append((start_time, stop_time))
    return output, times



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
    reactions = []
    contents = csv.reader(file, delimiter=',', quotechar='"')
    for n, row in enumerate(contents):
        time = row[TIME_IDX]
        time = time.split(".")[0] # Strip ms
        time = time.split(" ")[1] # Strip date
        time = datetime(*strptime(time, "%H:%M:%S")[0:6])
        reaction = row[RXN_IDX]
        reactions.append((reaction, time))
    return reactions




def plot_reaction_counts(counts):
    counts = sorted(counts)
    counts.reverse()
    pylab.scatter(range(0,len(counts)), counts)
    pylab.axis([-10, len(counts)+10, min(counts)-100, max(counts)+1000])
    pylab.xlabel('Turn')
    pylab.ylabel('Number of Reactions')
    pylab.title('Number of Reactions per Turn')
    pylab.show()



def count_reactions(turn_times, reactions):
    counts = []
    for i in range(len(turn_times)):
        count = 0
        start = turn_times[i][0]
        stop = turn_times[i][1]
        for j in range(len(reactions)):
            reaction_time = reactions[j][1]
            if stop > reaction_time > start:
                count += 1
        counts.append(count)
    return counts


# LABELING METHODS #####################################################################################################

# Label = low (0) / medium (1) / high (2) number of reactions:
def LABEL_by_count(times, reactions):
    counts = count_reactions(times, reactions)
    labels = []
    for i in range(len(counts)):
        count = counts[i]
        if count == 0:
            labels.append(0)
        elif count < 1000:
            labels.append(1)
        else:
            labels.append(2)

    return labels


# Label = majority agree, majority disagree, neutral
def LABEL_by_agreement(times, reactions):
    pass

# Label =
def LABEL_by_spin_dodge(times, reactions):
    pass


# Label = majority reaction (ex, "Romney:disagree")
def LABEL_by_everything(times, reactions):
    pass

########################################################################################################################

def main():
    rfile = 'resources/data/reactions_oct3_4project.csv'
    reactions = rxns(rfile)
    path = "resources/corpora/"
    filename = path + "oct3_coded_transcript_sync.csv"


    topics = topic_info(filename)
    data, times = read_data(filename, topics)



    #plot_reaction_counts(counts)
    labels = LABEL_by_count(times, reactions)


    # Write features to file:
    out = open("topicinfo.csv", 'w')
    for i in range(len(data)):
        out.write(str(labels[i]) + "\t")
        features = data[i]
        for j in range(len(features)-1):
            # Use topic ID as feature name:
            out.write(str(topics[j]) + ":" + str(features[j]) + "\t")
        #out.write(str("majority") + ":" + '"' + str(features[-1]) + '"')
        out.write('\n')



if __name__ == "__main__":
    main()