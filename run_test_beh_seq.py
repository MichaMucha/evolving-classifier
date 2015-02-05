__author__ = 'michalmucha'
import csv
from collections import defaultdict
from datetime import datetime

import multiprocessing as mp
from multiprocessing import Pool

from EVABCD import Classifier, SequenceOfActions, Action


TEST_DATA_FILENAME = 'behavior_sequence/test'
SUBSEQUENCE_LENGTH = 3
PROMPT = False
RECURSIVE = True
REPETITIONS = 1


def run():
    # load sequence
    # assign all sequences to user objects
    # add these sequences to EVABCD
    # run EVABCD

    EVABCD_Classifier = Classifier(subsequenceLength=SUBSEQUENCE_LENGTH, recursive=RECURSIVE)

    sequences = [1, 'ls', datetime.now()]

    def newEmptySequence():
        newempty = SequenceOfActions()
        return newempty
    sequences = defaultdict(newEmptySequence)
    with open(TEST_DATA_FILENAME, 'r', encoding='utf-8') as f:
        r = csv.reader(f, delimiter=',')
        for row in r:
            userID = int(row[0])
            sequences[userID].addAction(Action(''.join(row[1:])))

    # for i, u in enumerate(sequences.keys()):
    #     print(u, ':', ', '.join([str(x) for x in sequences[u].actions]))
    #     if i > 10:
    #         break
    for i in range(REPETITIONS):
        for userID in sequences.keys():
            EVABCD_Classifier.evolve(userID, sequences[userID])
            if PROMPT:
                print(EVABCD_Classifier)
                input('enter to continue')


    print('FINISHED EVOLUTIONS')
    # print(EVABCD_Classifier)

    # EVABCD_Classifier.classifyAll()
    EVABCD_Classifier.classifyAllMP()
    EVABCD_Classifier.writeReport('report_beh_seq.txt')


if __name__ == '__main__':
    run()