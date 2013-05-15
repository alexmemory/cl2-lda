# Isaac Julien
# Mallet partial interface

import os



class Mallet:

    def __init__(self):
        self.mallet_directory = "../mallet-2.0.7/" # Mallet code directory (not including /bin/)

        self.text_examples_file = "examples_file.txt" # Text file used to store examples line by line
        self.mallet_examples_file = "examples_file.mallet" # File used by mallet

        self.xval_k = 10 # K for K-fold xval

        self.trainer = "DecisionTree" # Training algorithm to use


    # Form a Mallet-readable line where the first field is a name for the example,
    # the second is a label, and the rest are features:
    def __form_line(self, label, features):
        line = str(label)
        for i in range(len(features)):
            line +=  "\t" + str(i) + ":" + str(features[i])
        return line

    # Write examples (in dictionary format) to file:
    def __write_to_file(self, examples):
        f = open(self.text_examples_file, 'w')
        for ex in examples:
            line = self.__form_line(ex["label"], ex["features"])
            f.write(line + "\n")


    # Read file into mallet and output to mallet_examples_file:
    def read_into_mallet(self, infile):
        command = self.mallet_directory + "bin/mallet import-svmlight --input " + infile + \
                  " --output " + self.mallet_examples_file
        self.__run_command(command)


    # Classify data with training portion and trainer specified above
    def classify(self):
        command = self.mallet_directory + "bin/mallet train-classifier " + \
                  "--input " + self.mallet_examples_file + " " + \
                  "--cross-validation " + str(self.xval_k) + " --trainer " + self.trainer + \
                  " --trainer MaxEnt --trainer NaiveBayes --verbosity 4"
        self.__run_command(command)


    def classify_options(self):
        command = self.mallet_directory + "bin/mallet train-classifier --help"
        self.__run_command(command)



    # Run a command:
    def __run_command(self, command):
        os.system(command)



    def test(self):
        exs = []
        for i in range(30):
            ex1 = {"label":0, "features":[0.0]}
            ex2 = {"label":1, "features":[1.0]}
            exs.append(ex1)
            exs.append(ex2)
        self.__write_to_file(exs)
        self.read_into_mallet("examples_file.txt")
        self.classify()



def classify():
    mallet = Mallet()
    mallet.read_into_mallet("topicinfo.csv")
    mallet.classify()


def options():
    Mallet().classify_options()


def main():
    #options()
    classify()


if __name__ == "__main__":
    main()