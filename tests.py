__author__ = 'michalmucha'

import unittest
import csv
from datetime import datetime, timedelta

import EVABCD


class TestTrie(unittest.TestCase):

    def setUp(self):

        a1 = EVABCD.Action('HH', datetime.now() - timedelta(days=4))
        a2 = EVABCD.Action('BH', datetime.now() - timedelta(days=3))
        a3 = EVABCD.Action('AS', datetime.now() - timedelta(days=2))
        a4 = EVABCD.Action('DR', datetime.now() - timedelta(days=1))


        self.a1 = a1
        self.a2 = a2
        self.a3 = a3
        self.a4 = a4

        actions = [a1, a2, a3, a4]

        sequenceOfActions = EVABCD.SequenceOfActions(actions)
        self.u = EVABCD.User(userID=5, sequenceOfActions=sequenceOfActions)



        db = []
        with open('test_sequence.csv', 'r', encoding='utf-8') as f:
            r = csv.reader(f, delimiter=';')
            next(r)
            for row in r:
                row[2] = datetime.strptime(row[2],"%d/%m/%Y %H:%M:%S")
                db.append(row)

        self.testSequence = db

        self.classifier = EVABCD.Classifier(recursive=False)
        self.recursiveClassifier = EVABCD.Classifier()
        # print(db[:3])


    # def testSequence(self):
    #     a1 = self.a1
    #     a2 = self.a2
    #     a3 = self.a3
    #     a4 = self.a4
    #
    #     self.assertEqual(self.u.sequenceOfActions.actions, [a1,a2,a3,a4])
    #     self.assertEqual(self.u.sequenceOfActions.subsequences(4), self.u.sequenceOfActions.actions)
    #     self.assertEqual(self.u.sequenceOfActions.subsequences(7), self.u.sequenceOfActions.actions)
    #     self.assertTrue(len(self.u.sequenceOfActions.subsequences(3)) == 2)
    #     self.assertEqual(self.u.sequenceOfActions.subsequences(3), [self.u.sequenceOfActions.actions[:3], self.u.sequenceOfActions.actions[1:]])
    #     self.assertEqual(self.u.sequenceOfActions.subsequences(2), [self.u.sequenceOfActions.actions[:2], self.u.sequenceOfActions.actions[1:3], self.u.sequenceOfActions.actions[2:]])

    def testTrie(self):
        t = self.u.trie
        t.printTrie()

    def testTrieExampleFromPaper(self):
        a1 = EVABCD.Action('ls', datetime.now())
        a2 = EVABCD.Action('date', datetime.now())
        a3 = EVABCD.Action('ls', datetime.now())
        a4 = EVABCD.Action('date', datetime.now())
        a5 = EVABCD.Action('cat', datetime.now())

        s = EVABCD.SequenceOfActions([a1,a2,a3,a4,a5])
        t = EVABCD.Trie(s, 3)
        print('\n\n-------')
        t.printTrie()

    def testProbabilityProfile(self):
        a1 = EVABCD.Action('ls', datetime.now())
        a2 = EVABCD.Action('date', datetime.now())
        a3 = EVABCD.Action('ls', datetime.now())
        a4 = EVABCD.Action('date', datetime.now())
        a5 = EVABCD.Action('cat', datetime.now())

        s = EVABCD.SequenceOfActions([a1,a2,a3,a4,a5])
        t = EVABCD.Trie(s, 3)

        pp = t.createFrequencyProfile()
        print ('\n\n------ Prob. profile -----\n')
        for sequence, probability in pp.items():
            print('%s : %s' % (sequence, probability))

        print ('\n ------ end ------\n')

        self.assertAlmostEqual(pp['ls'], 4/9)
        self.assertAlmostEqual(pp['date'], 4/9)
        self.assertAlmostEqual(pp['ls-date-ls'], 1/3)
        self.assertAlmostEqual(pp['date-ls'], 1/3)
        self.assertAlmostEqual(pp['ls-date'], 1/2)

        #test 0 for a sequence not recorded.
        self.assertAlmostEqual(pp['this-is-a-command-sequence-that-did-not-happen'], 0)


        #----------------------

    def testAddUpdateUserIteratively(self):
        userID = 1
        u1 = [EVABCD.Action(x[1],x[2]) for x in self.testSequence if int(x[0]) == userID]

        # dodanie tylko pierwszych 10 z 25 wpisów z bazy
        self.classifier.addOrUpdateUser(userID, EVABCD.SequenceOfActions(u1[:10]))

        p = self.classifier.users[userID].frequencyProfile
        self.assertAlmostEqual(p['hdh-hew-heh'], 1/8)
        self.assertAlmostEqual(p['hdh-hew-heh'], 1/8)
        self.assertAlmostEqual(p['heh-hnw-onn'], 1/8)

        self.assertAlmostEqual(p['hew-heh'], 4/16)
        self.assertAlmostEqual(p['heh-heh'], 2/16)
        self.assertAlmostEqual(p['hnw-onn'], 1/16)

        self.assertAlmostEqual(p['onn'], 1/24)
        self.assertAlmostEqual(p['heh'], 9/24)
        self.assertAlmostEqual(p['hnw'], 5/24)

        # dodanie pozostałych 25 wpisów z bazy
        self.classifier.addOrUpdateUser(userID, EVABCD.SequenceOfActions(u1[10:]))

        print ('\n ------ Test adding users - Trie after updating------\n')

        self.classifier.users[userID].trie.printTrie()

        print ('\n\n------ Test adding users - Probability profile -----\n')
        p = self.classifier.users[userID].frequencyProfile
        for sequence, probability in p.items():
            print('%s : %s' % (sequence, '%.4f' % probability))

        print ('\n ------ end ------\n')

    def testRegistryOfEncounteredSequences(self):
        userID = 1
        u1 = [EVABCD.Action(x[1],x[2]) for x in self.testSequence if int(x[0]) == userID]
        self.classifier.addOrUpdateUser(userID, EVABCD.SequenceOfActions(u1[:10]))
        

        reg = self.classifier.registryOfEncounteredSubsequences.keys()

        self.assertEqual(len(reg), 21, 'Invalid number of encountered subsequences')
        self.assertTrue('heh-hnw-onn' in reg)

        userID = 2
        u1 = [EVABCD.Action(x[1],x[2]) for x in self.testSequence if int(x[0]) == userID]
        self.classifier.addOrUpdateUser(userID, EVABCD.SequenceOfActions(u1[:10]))
        

        reg = self.classifier.registryOfEncounteredSubsequences.keys()
        self.assertTrue('onn-wen-hdw' in reg)
        self.assertTrue('wen-wdh' in reg)

    def testAddPrototypes(self):

        userID = 1
        u1 = [EVABCD.Action(x[1],x[2]) for x in self.testSequence if int(x[0]) == userID]
        self.classifier.addOrUpdateUser(userID, EVABCD.SequenceOfActions(u1[:10]))
        #self.addOrUpdateUserRecursively(userID, sequenceOfActions)
        
        self.classifier.classifyProfile(userID)

        self.assertTrue(len(self.classifier.prototypes), 1)
        self.assertEqual(self.classifier.prototypes[0].frequencyProfile, self.classifier.users[userID].frequencyProfile)

    def testClassifyProfile(self):
        userID = 1
        u1 = [EVABCD.Action(x[1],x[2]) for x in self.testSequence if int(x[0]) == userID]
        self.classifier.addOrUpdateUser(userID, EVABCD.SequenceOfActions(u1[:10]))
        #self.addOrUpdateUserRecursively(userID, sequenceOfActions)
        
        self.classifier.classifyProfile(userID)

        self.assertTrue(len(self.classifier.prototypes), 1)
        self.assertEqual(self.classifier.prototypes[0].frequencyProfile, self.classifier.users[userID].frequencyProfile)

        userID = 2
        u1 = [EVABCD.Action(x[1],x[2]) for x in self.testSequence if int(x[0]) == userID]
        self.classifier.addOrUpdateUser(userID, EVABCD.SequenceOfActions(u1[:10]))
        

        self.classifier.classifyProfile(userID)

        # print(self.classifier.users[userID].assignedPrototype)
        self.assertEqual(self.classifier.users[userID].assignedPrototype, self.classifier.users[1].assignedPrototype)

    def testCosineDistance(self):
        # generated with online calculator and values from test_potential.csv
        # www.appliedsoftwaredesign.com/archives/cosine-similarity-calculator/
        # cosine similarity between user 1 and 2: 0.344378042003
        # cosine similarity between user 1 and 5: 0.283446535409
        # cosine similarity between user 2 and 5: 0.28552608049

        for userID in [1,2,5]:
            u1 = [EVABCD.Action(x[1],x[2]) for x in self.testSequence if int(x[0]) == userID]
            self.classifier.addOrUpdateUser(userID, EVABCD.SequenceOfActions(u1))
            

        user1profile = self.classifier.users[1].frequencyProfile
        user2profile = self.classifier.users[2].frequencyProfile
        user5profile = self.classifier.users[5].frequencyProfile

        distance = self.classifier.cosDistBetweenTwoSamples(user1profile,user2profile)
        self.assertAlmostEqual(distance, 1 - 0.344378042003)
        distance = self.classifier.cosDistBetweenTwoSamples(user1profile,user5profile)
        self.assertAlmostEqual(distance, 1 - 0.283446535409)
        distance = self.classifier.cosDistBetweenTwoSamples(user2profile,user5profile)
        self.assertAlmostEqual(distance, 1 - 0.28552608049)
        print(1 - 0.344378042003, 1 - 0.283446535409, 1 - 0.28552608049)

    def testCalculateProfilePotentialIteratively(self):

        for userID in [1,2,5]:
            u1 = [EVABCD.Action(x[1],x[2]) for x in self.testSequence if int(x[0]) == userID]
            self.classifier.addOrUpdateUser(userID, EVABCD.SequenceOfActions(u1))
            

        P1 = self.classifier.calculateProfilePotentialIteratively(1)
        P2 = self.classifier.calculateProfilePotentialIteratively(2)
        P5 = self.classifier.calculateProfilePotentialIteratively(5)

        self.assertAlmostEqual(P1, 0.59308895575)
        self.assertAlmostEqual(P2, 0.59345492611)
        self.assertAlmostEqual(P5, 0.58291577889)

        print(P1, P2, P5)

    def testShowPrototypeRecalculationBehavior(self):

        for userID in [1,2,5]:
            u1 = [EVABCD.Action(x[1],x[2]) for x in self.testSequence if int(x[0]) == userID]
            self.classifier.addOrUpdateUser(userID, EVABCD.SequenceOfActions(u1))
            
            self.classifier.classifyProfile(userID)
            self.classifier.users[userID].frequencyProfilePotential = self.classifier.calculateProfilePotentialIteratively(userID)
            for proto in self.classifier.prototypes:
                print('Prototype potential: %f (before recalculation)' % proto.frequencyProfilePotential)
            self.classifier.recalculatePrototypePotentials()

            if userID == 2:
                self.assertAlmostEqual(self.classifier.prototypes[0].frequencyProfilePotential, 0.6040026197)
            if userID == 5:
                self.assertAlmostEqual(self.classifier.prototypes[0].frequencyProfilePotential, 0.593089)

            for proto in self.classifier.prototypes:
                print('Prototype potential: %f (after recalculation)' % proto.frequencyProfilePotential)
            print('Users: %d, Prototypes: %d' % (len(self.classifier.users), len(self.classifier.prototypes)))

    def testEvaluateProfileForPrototype(self):

        for userID in [1,2,5,6,7,8,9,10]:
            u1 = [EVABCD.Action(x[1],x[2]) for x in self.testSequence if int(x[0]) == userID]
            self.classifier.addOrUpdateUser(userID, EVABCD.SequenceOfActions(u1))
            
            self.classifier.classifyProfile(userID)
            P = self.classifier.calculateProfilePotentialIteratively(userID)
            self.classifier.users[userID].frequencyProfilePotential = P
            for proto in self.classifier.prototypes:
                print('\nPrototype potential: %f (before recalculation)' % proto.frequencyProfilePotential)
            self.classifier.recalculatePrototypePotentials()
            for proto in self.classifier.prototypes:
                print('Prototype potential: %f (after recalculation)' % proto.frequencyProfilePotential)
            for user in self.classifier.users.values():
                print('Potential of user: %f' % user.frequencyProfilePotential)
            print('\nUsers: %d, Prototypes: %d  (before addition)' % (len(self.classifier.users), len(self.classifier.prototypes)))
            if self.classifier.evaluateProfileForPrototype(P):
                print('---- New prototype found! ----')
                self.classifier.addPrototype(userID)

            print('Users: %d, Prototypes: %d  (after addition)' % (len(self.classifier.users), len(self.classifier.prototypes)))

        self.assertTrue(len(self.classifier.prototypes) == 3)

    def testPrototypeRemoval(self):

        for userID in [1,2,5,6,7,8,9,10]:
            u1 = [EVABCD.Action(x[1],x[2]) for x in self.testSequence if int(x[0]) == userID]
            self.classifier.addOrUpdateUser(userID, EVABCD.SequenceOfActions(u1))
            
            self.classifier.classifyProfile(userID)
            P = self.classifier.calculateProfilePotentialIteratively(userID)
            self.classifier.users[userID].frequencyProfilePotential = P
            for proto in self.classifier.prototypes:
                print('\nPrototype potential: %f (before recalculation)' % proto.frequencyProfilePotential)
            self.classifier.recalculatePrototypePotentials()
            for proto in self.classifier.prototypes:
                print('Prototype potential: %f (after recalculation)' % proto.frequencyProfilePotential)
            for user in self.classifier.users.values():
                print('Potential of user: %f' % user.frequencyProfilePotential)
            print('\nUsers: %d, Prototypes: %d  (before addition)' % (len(self.classifier.users), len(self.classifier.prototypes)))
            if self.classifier.evaluateProfileForPrototype(P):
                print('---- New prototype found! ----')
                l = len(self.classifier.prototypes)
                self.classifier.evaluatePrototypesForRemovingAndRemove(userID)
                self.classifier.addPrototype(userID)
                if l > len(self.classifier.prototypes) - 1 :
                    print('---- One of the old prototypes removed! ----')
                    for proto in self.classifier.prototypes:
                        print('Prototype potential: %f (after removals)' % proto.frequencyProfilePotential)
                    for user in self.classifier.users.values():
                        print(user.assignedPrototype)

            print('Users: %d, Prototypes: %d  (after addition)' % (len(self.classifier.users), len(self.classifier.prototypes)))

        self.assertTrue(len(self.classifier.prototypes) == 1)

# --------------- RECURSIVE ---------------

    def testAddUpdateUserRecursively(self):
        userID = 1
        u1 = [EVABCD.Action(x[1],x[2]) for x in self.testSequence if int(x[0]) == userID]

        # dodanie tylko pierwszych 10 z 25 wpisów z bazy
        self.recursiveClassifier.addOrUpdateUserRecursively(userID, EVABCD.SequenceOfActions(u1[:10]))

        p = self.recursiveClassifier.users[userID].frequencyProfile
        self.assertAlmostEqual(p['hdh-hew-heh'], 1/8)
        self.assertAlmostEqual(p['hdh-hew-heh'], 1/8)
        self.assertAlmostEqual(p['heh-hnw-onn'], 1/8)

        self.assertAlmostEqual(p['hew-heh'], 4/16)
        self.assertAlmostEqual(p['heh-heh'], 2/16)
        self.assertAlmostEqual(p['hnw-onn'], 1/16)

        self.assertAlmostEqual(p['onn'], 1/24)
        self.assertAlmostEqual(p['heh'], 9/24)
        self.assertAlmostEqual(p['hnw'], 5/24)

        # dodanie pozostałych 25 wpisów z bazy
        self.recursiveClassifier.addOrUpdateUser(userID, EVABCD.SequenceOfActions(u1[10:]))

        print ('\n ------ Test adding users - Trie after updating------\n')

        self.recursiveClassifier.users[userID].trie.printTrie()

        print ('\n\n------ Test adding users - Probability profile -----\n')
        p = self.recursiveClassifier.users[userID].frequencyProfile
        for sequence, probability in p.items():
            print('%s : %s' % (sequence, '%.4f' % probability))

        print ('\n ------ end ------\n')

        self.assertAlmostEqual(p['onh-hdw-onw'], 1/16)
        self.assertAlmostEqual(p['hew-hnw-hew'], 1/16)
        self.assertAlmostEqual(p['heh-hnw-onn'], 1/16)

        self.assertAlmostEqual(p['hdh-hew'], 1/32)
        self.assertAlmostEqual(p['heh-heh'], 1/16)
        self.assertAlmostEqual(p['hdw-onw'], 1/16)

        self.assertAlmostEqual(p['onw'], 1/8)
        self.assertAlmostEqual(p['hew'], 1/6)
        self.assertAlmostEqual(p['wdn'], 1/24)

    def testCalculateProfilePotentialRecursively(self):
    # TODO: Error happens when the classifier gets sequences from only one user more than once after initialization

        for userID in [1,2,5]:
            u1 = [EVABCD.Action(x[1],x[2]) for x in self.testSequence if int(x[0]) == userID]
            self.recursiveClassifier.evolve(userID, EVABCD.SequenceOfActions(u1[:5]))
            print('User ID %d, potential: %d' %(userID, self.recursiveClassifier.users[userID].frequencyProfilePotential))
        for userID in [1,2,5]:
            u1 = [EVABCD.Action(x[1],x[2]) for x in self.testSequence if int(x[0]) == userID]
            self.recursiveClassifier.evolve(userID, EVABCD.SequenceOfActions(u1[5:15]))
            print('User ID %d, potential: %d' %(userID, self.recursiveClassifier.users[userID].frequencyProfilePotential))
        for userID in [1,2,5]:
            u1 = [EVABCD.Action(x[1],x[2]) for x in self.testSequence if int(x[0]) == userID]
            self.recursiveClassifier.evolve(userID, EVABCD.SequenceOfActions(u1[15:]))
            print('User ID %d, potential: %d' %(userID, self.recursiveClassifier.users[userID].frequencyProfilePotential))


        P1 = self.recursiveClassifier.users[1].frequencyProfilePotential
        P2 = self.recursiveClassifier.users[2].frequencyProfilePotential
        P5 = self.recursiveClassifier.users[5].frequencyProfilePotential
        print(P1, P2, P5)

        self.assertAlmostEqual(P1, 0.70047128215)
        self.assertAlmostEqual(P2, 0.70376897678)
        self.assertAlmostEqual(P5, 0.70768951032)

    def CompareIterativePotentialsAndRecursivePotentials(self):

        for userID in [1,2,5]:
            u1 = [EVABCD.Action(x[1],x[2]) for x in self.testSequence if int(x[0]) == userID]
            self.recursiveClassifier.evolve(userID, EVABCD.SequenceOfActions(u1[:5]))
            print('\nRECURSIVE: User ID %d, potential: %f' %(userID, self.recursiveClassifier.users[userID].frequencyProfilePotential))
            self.classifier.evolve(userID, EVABCD.SequenceOfActions(u1[:5]))
            print('ITERATIVE: User ID %d, potential: %f' %(userID, self.classifier.users[userID].frequencyProfilePotential))
        for userID in [1,2,5]:
            u1 = [EVABCD.Action(x[1],x[2]) for x in self.testSequence if int(x[0]) == userID]
            self.recursiveClassifier.evolve(userID, EVABCD.SequenceOfActions(u1[5:15]))
            print('\nRECURSIVE: User ID %d, potential: %f' %(userID, self.recursiveClassifier.users[userID].frequencyProfilePotential))
            self.classifier.evolve(userID, EVABCD.SequenceOfActions(u1[5:15]))
            print('ITERATIVE: User ID %d, potential: %f' %(userID, self.classifier.users[userID].frequencyProfilePotential))
        for userID in [1,2,5]:
            u1 = [EVABCD.Action(x[1],x[2]) for x in self.testSequence if int(x[0]) == userID]
            self.recursiveClassifier.evolve(userID, EVABCD.SequenceOfActions(u1[15:]))
            print('\nRECURSIVE: User ID %d, potential: %f' %(userID, self.recursiveClassifier.users[userID].frequencyProfilePotential))
            self.classifier.evolve(userID, EVABCD.SequenceOfActions(u1[15:]))
            print('ITERATIVE: User ID %d, potential: %f' %(userID, self.classifier.users[userID].frequencyProfilePotential))

        # TODO: Error happens when the classifier gets sequences from only one user more than once after initialization
        # for userID in [1,2,5]:
        #     u1 = [EVABCD.Action(x[1],x[2]) for x in self.testSequence if int(x[0]) == userID]
        #     self.recursiveClassifier.evolve(userID, EVABCD.SequenceOfActions(u1[:5]))
        #     print('User ID %d, potential: %f' %(userID, self.recursiveClassifier.users[userID].frequencyProfilePotential))
        #     self.recursiveClassifier.evolve(userID, EVABCD.SequenceOfActions(u1[5:15]))
        #     print('User ID %d, potential: %f' %(userID, self.recursiveClassifier.users[userID].frequencyProfilePotential))
        #     self.recursiveClassifier.evolve(userID, EVABCD.SequenceOfActions(u1[15:]))
        #     print('User ID %d, potential: %f' %(userID, self.recursiveClassifier.users[userID].frequencyProfilePotential))

        P1 = self.recursiveClassifier.users[1].frequencyProfilePotential
        P2 = self.recursiveClassifier.users[2].frequencyProfilePotential
        P5 = self.recursiveClassifier.users[5].frequencyProfilePotential

        IP1 = self.classifier.users[1].frequencyProfilePotential
        IP2 = self.classifier.users[2].frequencyProfilePotential
        IP5 = self.classifier.users[5].frequencyProfilePotential

        self.assertAlmostEqual(P1, IP1)
        self.assertAlmostEqual(P2, IP2)
        self.assertAlmostEqual(P5, IP5)

if __name__ == '__main__':
    unittest.main()
