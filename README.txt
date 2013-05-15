


Classifying turns by Boydstun-labeled topics - topicinfo.py, mallet.py
----------------------------------------------------------------------

Dependencies: Python 2.7, uses scipy
 	      Mallet installed (http://mallet.cs.umass.edu/)

topicinfo.py builds feature and label files for mallet.py to use for classification, based on the Boydstun labeled topics. mallet.py is run after topicinfo.py, and prints out the results of classifying the output of topicinfo.py using Mallet. A sample run would look like this:

$ python topicinfo.py
$ python mallet.py
  ...
  (mallet.py output)
  ...

mallet.py requires that Mallet be installed. At the top of mallet.py, there is a line:
self.mallet_directory = "../mallet-2.0.7/"
This should be changed to the directory of wherever Mallet is installed.

topicinfo.py requires the debates reactions and transcript corpora. It assumes that the path to the debate reactions corpus is "resources/data/reactions_oct3_4project.csv" and that the path to the transcript is "resources/corpora/oct3_coded_transcript_sync.csv".

In the main() method of topicinfo.py, there is a line:

labels = LABEL_by_spin_dodge(turn_info, reactions_Romney)

The method LABEL_by_spin_dodge creates labels based on the number of spin and dodge reactions. There are two other methods for labeling: LABEL_by_agreement(), which creates labels based on the number of reactions agreeing and disagreeing with the current speaker, and LABEL_by_count(), which creates labels based on the total number of reactions.

The second argument to the method, "reactions_Romney," is the set of reactions by users who support Romney. To change it to the set of users who support Obama, replace it with "reactions_Obama."





Classifying individual users' reactions - topicinfo2.py, mallet.py
----------------------------------------------------------------------

As before, topicinfo2.py generates files of features and labels for mallet.py to use, and assumes the same existence and location of the debates corpora. A sample run would look like this:

$ python topicinfo2.py
  Skipped 2499 data points with missing information.
  Got 190787 useable data points.
$ python mallet.py
  ...
  (mallet output)
  ... 

The output of mallet.py will be the results of 12-way classification, for each possible individual reaction.



Classifying turns by N-Gram features - baseline_ngrams.py
----------------------------------------------------------------------

Dependencies: Python 2.7, NumPy 1.6.1, Pandas 0.10.1, NLTK 2.0.4

    This has been tested with Enthought Python Distribution (EPD) Free 7.3-2. Other dependencies may
    exist that are not satisfied if a different Python distribution is used to run this software.

To run, do the following:

$ python baseline_ngrams.py <path to reactions CSV file> <path to coded transcript CSV file> <unigram/bigram>

Example:

$ python baseline_ngrams.py data/reactions_oct3_4project.csv corpora/oct3_coded_transcript_sync.csv unigram

The program will display the results (mean and std dev of accuracies) of the n-grams evaluation to the console.
