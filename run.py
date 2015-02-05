__author__ = 'michalmucha'
import datetime
import sys
import csv
from collections import defaultdict

from EVABCD import Classifier, SequenceOfActions, Action


DIR_PATH_FOR_REPORTS = 'reports/'
SUBSEQUENCE_LENGTH = 3
BATCH_SIZE = 10000
REPORT_FREQ = 10 #REPORT EVERY X'th BATCH
RECURSIVE=False
# total entries for m / 31 = 24030736

def process_row(r):
    user_id = int(r[0])
    # action = Action(''.join(r[1:]))
    action = Action(''.join(r[1:3]))
    return user_id, action


if __name__ == '__main__':
    behavior_sequence_filenames = sys.argv[1:]

    classifier = Classifier(recursive=RECURSIVE, subsequenceLength=SUBSEQUENCE_LENGTH)

    for filename in behavior_sequence_filenames:

        # open file specified in args
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                re = csv.reader(file)

                batch_of_sequences = defaultdict(lambda : SequenceOfActions())
                batch = 1
                i = 0

                for r in re:

                    i+=1
                    if i == BATCH_SIZE:
                        # evolve the classifier with all k, v pairs in the dict
                        #
                        print(datetime.datetime.now(), 'Running classifier on batch', batch,
                              'containing', len(batch_of_sequences), 'users')
                        k = 0
                        for uid, sequence in batch_of_sequences.items():
                            classifier.evolve(uid, sequence)
                            k+=1
                            if k % 500 == 0:
                                print(datetime.datetime.now(), 'Processed', '%.1f' % (k/1000),
                                      'thousand users from batch', batch)

                        # flush batch data
                        batch_of_sequences = defaultdict(lambda : SequenceOfActions())

                        # classify all, print report
                        if batch % REPORT_FREQ == 0:
                            print(datetime.datetime.now(), 'Classifying all users into prototypes. There are',
                                  len(classifier.prototypes), 'prototypes')
                            classifier.classifyAll()
                            print(datetime.datetime.now(), 'Writing report')
                            classifier.writeReport(DIR_PATH_FOR_REPORTS + ('report_batch%04d.txt' % batch))

                        # repeat with the next batch
                        i = 0
                        batch += 1
                        print(datetime.datetime.now(), 'Processing next batch - batch no.', batch)

                    # print status
                    if i % 10000 == 0:
                        print(datetime.datetime.now(), '- batch %d - %dk rows' % (batch, i//1000))

                    # load a batch of rows
                    try:
                        # process the rows into a dict : user_id as key, SequenceOfActions as value
                        user_id, action = process_row(r)
                        batch_of_sequences[user_id].addAction(action)

                    except Exception as e:
                        print('Error processing row:', e)

                for uid, sequence in batch_of_sequences.items():
                    classifier.evolve(uid, sequence)

                classifier.classifyAll()
                classifier.writeReport(DIR_PATH_FOR_REPORTS + 'report_batch_final.txt')

        except Exception as e:
            print('Error loading file', e)











