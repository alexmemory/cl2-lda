cl2-lda
=======

# Preprocessing

## Extracting conversation turns from debate corpora

Text from turns in the debate corpora and metadata related to those turns can be extracted with format.py. This script can be run from the command line as follows:

`python format.py output_name input.json`

`output_name` specifies the prefix of three files created by the script: output_name/ (a directory of bags of words usable by mallet), output_name.train (metadata for each document in the training set), and output_name.test. The first field in output_name.* is an id number which is also the name of the corresponding bag of words in the output_name/ directory. The subsequent fields are the speaker id, turn start timestamp, turn stop timestamp, question topic, turn topic, the mode of the turn frames, and the mode of the turn tone.

`input.json` is a json file with information about each corpus (file name, whether is it for training or testing, indices for relevant columns in the csv corpus). For more details, look at input_example.txt.
