__author__ = 'michalmucha'
import csv
from datetime import datetime

from EVABCD import Classifier, SequenceOfActions, Action



# TEST_DATA_FILENAME = 'long_test_sequence2.csv'
TEST_DATA_FILENAME = 'testcase/sequence-1.csv'
USERS = 60
SEQUENCE_LENGTH = 25
SUBSEQUENCE_LENGTH = 4
PROMPT = False
RECURSIVE = True
REPETITIONS = 2


def run():
    # load sequence
    # assign all sequences to user objects
    # add these sequences to EVABCD
    # run EVABCD

# INPUT FORMAT:
# [ userID , sequenceElementValue , timestamp ]
    EVABCD_Classifier = Classifier(subsequenceLength=SUBSEQUENCE_LENGTH, recursive=RECURSIVE)

    sequence = [1, 'ls', datetime.now()]
    
    sequence = []
    with open(TEST_DATA_FILENAME, 'r', encoding='utf-8') as f:
        r = csv.reader(f, delimiter=';')
        next(r)
        for row in r:
            row[2] = datetime.strptime(row[2],"%d/%m/%Y %H:%M:%S")
            sequence.append(row)

    for i in range(REPETITIONS):
        for userID in range(1,36):
            actions = [Action(x[1],x[2]) for x in sequence if int(x[0]) == userID]
            EVABCD_Classifier.evolve(userID, SequenceOfActions(actions))
            if PROMPT:
                print(EVABCD_Classifier)
                input('enter to continue')

        for userID in range(36,USERS+1):
            actions = [Action(x[1],x[2]) for x in sequence if int(x[0]) == userID]
            EVABCD_Classifier.evolve(userID, SequenceOfActions(actions[:14]))
            if PROMPT:
                print(EVABCD_Classifier)
                input('enter to continue')

    print('FINISHED EVOLUTIONS')
    print(EVABCD_Classifier)

    EVABCD_Classifier.classifyAll()
    EVABCD_Classifier.writeReport('report_rts.txt')


if __name__ == '__main__':
    run()