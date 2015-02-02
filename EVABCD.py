__author__ = 'michalmucha'

from collections import defaultdict
from math import sqrt, exp, pi
from statistics import mean

from cosineDistance import cosine_distance


CONST_S = 1 / sqrt(2*pi)

class Prototype:

    def __init__(self, user, prototypeID, label = ''):
        self.id = prototypeID
        self.label = label # artificial label
        self.frequencyProfile = user.frequencyProfile
        self.frequencyProfilePotential = user.frequencyProfilePotential
        self.originalUser = user.id
        self.numberOfUsersAssigned = 1
        # print(self.originalUser)

    def __str__(self):
        s = 'Prototype %d (based on user ID%d, potential %f' % (self.id, self.originalUser, self.frequencyProfilePotential)
        return  s

class User: # User with an ID, his sequence, his profile that comes from the sequence, and his classified prototype

    def __init__(self, userID, sequenceOfActions, subsequenceLength = 3):
        self.id = userID
        self.assignedPrototype = None
        self.subsequenceLength = subsequenceLength

        self.trie = Trie(sequenceOfActions, subsequenceLength)
        # print('\n', 150*'#','\nTRIE FOR USER',self.id,'\n')
        # self.trie.printTrie()
        # print('END\n\n',150*'#')
        self.frequencyProfile = self.trie.createFrequencyProfile()
        self.recursiveSequenceDescriptors = defaultdict(int)
        self.calculateRecursiveSequenceDescriptors()
        self.frequencyProfilePotential = 1

        self.recursiveSigmas = defaultdict(lambda : int(1))

        self.recursiveIteration = 0

        self.memoryFromLastSequence = []

    def __str__(self):
        s = 'User ID %d, with freq potential %f \t- assigned to prototype: %s' % (self.id, self.frequencyProfilePotential, self.assignedPrototype)
        return  s

    def update(self, newSequenceOfActions):
        newSequenceOfActions.appendInFront(self.memoryFromLastSequence)
        self.memoryFromLastSequence = newSequenceOfActions.returnLastElements(self.subsequenceLength-1)

        self.trie.buildTrie(newSequenceOfActions)
        self.frequencyProfile = self.trie.createFrequencyProfile()

    def updateRecursively(self, newSequenceOfActions):
        newSequenceOfActions.appendInFront(self.memoryFromLastSequence)
        self.memoryFromLastSequence = newSequenceOfActions.returnLastElements(self.subsequenceLength-1)

        self.trie = Trie(newSequenceOfActions, self.subsequenceLength)
        self.frequencyProfile = self.trie.createFrequencyProfile()
        del self.trie



        self.calculateRecursiveSequenceDescriptors()
        self.recursiveIteration += 1

    def calculateRecursiveSequenceDescriptors(self):
        '''
        Recursive sequence descriptors are the lowercase b values from equation (5) in the EVABCD paper
        :return:
        '''
        sumOfSquaredProfileElements = sum([pow(x,2) for x in self.frequencyProfile.values()])
        for profileElement in self.frequencyProfile.keys():
            if self.frequencyProfile[profileElement] == 0:
                self.recursiveSequenceDescriptors[profileElement] += 0
            else:
                self.recursiveSequenceDescriptors[profileElement] += \
                    sqrt(pow(self.frequencyProfile[profileElement],2) / sumOfSquaredProfileElements)


    def updateProfilePotentialRecursively(self, numberOfDataSamples, allRegisteredSequences):
        '''
        Computationally easier, faster way of retrieving the potential, having updated the model with new sequences.
        This function performs the calculation described in formula (5) in the EVABCD research paper.
        :param numberOfDataSamples: the value corresponding to k in formula (5) in the EVABCD paper
        :param allRegisteredSequences: array of all sequences encountered by the classifier,
        n represents the total count in the formula (5)
        :return: the new potential
        '''

        if self.recursiveIteration == 1 and numberOfDataSamples == 1:
            return 1
        # if numberOfDataSamples == 1:
        #    numberOfDataSamples = 0.0001
        #     return 1
        # TODO: Error happens when the classifier gets sequences from only one user more than once after initialization

        z = self.frequencyProfile
        # self.calculateRecursiveSequenceDescriptors()
        b = self.recursiveSequenceDescriptors

        # sum of z_j^2
        sumOfSquaredProfileElements = sum([pow(x,2) for x in self.frequencyProfile.values()])
        B = 0
        for j in allRegisteredSequences:
            B += z[j] * b[j]

        try:
            P = 1 / \
            ( 2 - (1 / (numberOfDataSamples - 1)) * (1 / sqrt(sumOfSquaredProfileElements)) * B )
        except Exception as e:
            print('Recursive formula error - division by 0. Exception: %s' % e)
            P = 1
        # self.frequencyProfilePotential = P
        # TODO: due to errors in the formula
        # TODO: resulting from very small population size (second user with P=640), min(P,1) is introduced.
        # TODO: This is obviously a workaround and a true resolution should be introduced
        return min(P,1)

class Action:

    def __init__(self, value, timestamp = '1'):
        self.value = value
        self.timestamp = timestamp

    def __str__(self):
        return str(self.value)

class SequenceOfActions:

    def __init__(self, actions = list()):
        self.actions = actions[:] # list of tuples (value,timestamp)
        self.label = '' # artificial label for supervised

    def __str__(self):
        return str(self.actions)

    def addAction(self, action):
        self.actions.append(action)

    def appendInFront(self, a):
        if len(a) > 0:
            self.actions = a + self.actions

    def returnLastElements(self, k):
        return self.actions[-k:]

    def subsequences(self, subseqLen = 3):
        l = len(self.actions)
        if l <= subseqLen:
            return [self.actions[:]]
        else:
            return [self.actions[i:(i+subseqLen)] for i in range(0, l-subseqLen+1)]

class Trie:

    def __init__(self, sequence, subsequenceLength = 3):
        self.subsequenceLength = subsequenceLength
        self.nodes = defaultdict(lambda : TrieNode())
        self.buildTrie(sequence)

    def buildTrie(self, sequence):
        s = sequence.subsequences(self.subsequenceLength)
        for subseq in s:
            for i in range(0, len(subseq)):
                self.writeSubsequence(subseq[i:])

    def writeSubsequence(self, subsequence):
        actionValue = subsequence[0].value
        actionTimestamp = subsequence[0].timestamp
        currentNode = self.nodes[actionValue]
        currentNode.timestamps.append(actionTimestamp)

        for i in range(1,len(subsequence)):
            actionValue = subsequence[i].value
            actionTimestamp = subsequence[i].timestamp
            currentNode.children[actionValue].timestamps.append(actionTimestamp)
            currentNode = currentNode.children[actionValue] # go deeper

    def printTrie(self):
        for name, node in self.nodes.items():
            print('%s (%s)' % (name, len(node.timestamps)) )
            inset='\t'
            node.print(inset)

    def createFrequencyProfile(self): # Here you can create a limit on timestamps
        # { subsequence: 0.2 }
        # result to be achieved using trie's

        # first, walk the whole trie and get all sequences, along with their occurrences
        allSequences = []
        for name, node in self.nodes.items():
            allSequences.append(([name], len(node.timestamps))) # add one-item sequences
            node.createProfileSequence(allSequences, [name]) # get all leaves to add themselves and their leaves

        # print('\n\nsequences retrieved from trie, with their occurences:\n', *allSequences)

        # second, calculate the support values among sequences of different lengths

        maxSequenceLength = max([len(x[0]) for x in allSequences])

        frequencyProfile = defaultdict(int)
        for i in range(1, maxSequenceLength+1):
            allSequencesOfGivenLength = [x for x in allSequences if len(x[0]) == i]
            sumOfAllOccurrences = sum([x[1] for x in allSequencesOfGivenLength])
            for item in allSequencesOfGivenLength:
                frequencyProfile['-'.join(item[0])] = item[1] / float(sumOfAllOccurrences)

        return frequencyProfile

class TrieNode:

    def __init__(self):
        self.timestamps = []
        self.children = defaultdict(lambda : TrieNode())

    def print(self, inset):
        for name, node in self.children.items():
            print(inset+( '%s (%s)' % (name, len(node.timestamps))))
            node.print(inset+'\t')

    def createProfileSequence(self, allSequences, parentSequence):
        for name, node in self.children.items():
            allSequences.append((parentSequence + [name], len(node.timestamps)))
            node.createProfileSequence(allSequences, parentSequence + [name])



class Classifier:
    # when a set of new user sequences is added, for each sample.. (for each user that changed)
    #
    # 1. classify the sample to one of the exisiting prototypes,
    # 2. calculate the potential of this new data sample
    # 3. see if the new sample has the potential to become a prototype; add if yes
    # 4. see if any old prototypes overlap with the newly added; remove if yes

    def __init__(self, recursive = True, subsequenceLength = 3):
        self.prototypes = []
        self.prototypeIDcounter = 0
        self.evolutionCounter = 0
        self.users = {}
        self.registryOfEncounteredSubsequences = defaultdict(int)
        self.recursiveMode = recursive
        self.subsequenceLength = subsequenceLength

    def addOrUpdateUser(self, userID, sequenceOfActions):
        try:
            user = self.users[userID]
            user.update(sequenceOfActions)
        except:
            self.users[userID] = User(userID, sequenceOfActions, self.subsequenceLength)
        self.updateRegistryOfEncounteredSubsequences(userID)
        self.classifyProfile(userID)

    def addOrUpdateUserRecursively(self, userID, sequenceOfActions):
        try:
            user = self.users[userID]
            user.updateRecursively(sequenceOfActions)
        except:
            self.users[userID] = User(userID, sequenceOfActions, self.subsequenceLength)
        self.updateRegistryOfEncounteredSubsequences(userID)
        self.classifyProfile(userID)

    def updateRegistryOfEncounteredSubsequences(self, userID):
        for subsequence in self.users[userID].frequencyProfile.keys():
            self.registryOfEncounteredSubsequences[subsequence] = 1

    def updateProfilePotentialRecursively(self, userID):
        #x_k - k'th data sample = self.users[k].frequencyProfile
        numberOfSamples = len(self.users)
        return self.users[userID].updateProfilePotentialRecursively(numberOfSamples, self.registryOfEncounteredSubsequences.keys())

    def calculateProfilePotentialIteratively(self, userID):
        if len(self.users) == 1: return 1

        # TODO : optimize from O(n^2) to O(nlogn) by avoiding doublecounting
        #x_k - k'th data sample = self.users[k].frequencyProfile

        # k-1
        numberOfSamples = len(self.users)

        sumOfDistancesToAllSamples = 0
        for id in self.users.keys():
            if id != userID:
                sumOfDistancesToAllSamples += self.cosDistBetweenTwoSamples(self.users[userID].frequencyProfile,
                                                                                       self.users[id].frequencyProfile)

        P = 1 / (1 + sumOfDistancesToAllSamples / (numberOfSamples - 1))
        return P

    def recalculatePrototypePotentials(self):
        numberOfSamples = len(self.users)
        if numberOfSamples == 1: return

        for prototype in self.prototypes:
            sumOfDistancesToAllSamples = 0
            for id in self.users.keys():
                sumOfDistancesToAllSamples += self.cosDistBetweenTwoSamples(prototype.frequencyProfile,
                                                                            self.users[id].frequencyProfile)
            prototype.frequencyProfilePotential = 1 / (1 + sumOfDistancesToAllSamples / (numberOfSamples - 1))

    def recalculatePrototypePotentialsRecursively(self):
        numberOfSamples = len(self.users)
        if numberOfSamples == 1: return

        for prototype in self.prototypes:
            P = self.users[prototype.originalUser].updateProfilePotentialRecursively(numberOfSamples, self.registryOfEncounteredSubsequences.keys())
            prototype.frequencyProfilePotential = P

    def cosDistBetweenTwoSamples(self, userProfile1, userProfile2):
        user1_vector = []
        user2_vector = []
        for sequence in self.registryOfEncounteredSubsequences.keys():
            user1_vector.append(userProfile1[sequence])
            user2_vector.append(userProfile2[sequence])
        distance = cosine_distance(user1_vector, user2_vector)
        return distance


    def addPrototype(self, userID):
        self.prototypes.append(Prototype(self.users[userID], self.prototypeIDcounter))
        self.prototypeIDcounter += 1

    def evaluateProfileForPrototype(self, potential):
        for prototype in self.prototypes:
            if prototype.frequencyProfilePotential < potential:
                return True

        return False

    def calculateRecursiveSigmas(self, userID):
        k = len(self.users)
        for prototype in self.prototypes:
            oldValue = self.users[userID].recursiveSigmas[prototype.id]
            try:
                cosdist = self.cosDistBetweenTwoSamples(self.users[userID].frequencyProfile, prototype.frequencyProfile)
                newValue = sqrt(pow(oldValue, 2) + (pow(cosdist, 2) - pow(oldValue, 2))/k)
                if newValue == 0:
                    newValue+= 0.1
            except Exception as e:
                print('Recursive sigma calculation error:', e)
                newValue = 1
            self.users[userID].recursiveSigmas[prototype.id] = newValue

        # del self.users[userID].frequencyProfile

    def evaluatePrototypesForRemovingAndRemove(self, userID):
        # for all prototypes, see if micro(z_k) > e^-1
        # k = len(self.users) # numberOfSamples
        def determineForRemoval(prototype):
            # TODO: added ^2 to sigma on 22 Jan 2015
            if self.recursiveMode == False:
                sigma = sqrt( mean([self.cosDistBetweenTwoSamples(prototype.frequencyProfile, x.frequencyProfile) for x in self.users.values()]))
            else:
                sigma = self.users[userID].recursiveSigmas[prototype.id]
            micro = CONST_S/sigma * exp( (pow(self.cosDistBetweenTwoSamples(self.users[userID].frequencyProfile, prototype.frequencyProfile), 2) / sigma) / -2)
            # micro = exp( (pow(self.cosDistBetweenTwoSamples(self.users[userID].frequencyProfile, prototype.frequencyProfile), 2) / sigma) / -2)
            # print('Sigma: %f,\n\t\t Micro: %f   exp^-1: %f' % (sigma, micro, exp(-1)))
            if micro > exp(-1): return True
            else: return False

        newPrototypeList = [x for x in self.prototypes if not determineForRemoval(x)]
        # if len(newPrototypeList) < self.prototypes:
        #     print('Removing some prototypes.. Should we re-classify all?')
        #     markedForRemoval = list( set(self.prototypes) - set(newPrototypeList) )
        self.prototypes[:] = newPrototypeList

    def classifyProfile(self, userID):
        if len(self.prototypes) == 0:
            self.addPrototype(userID)
            self.users[userID].assignedPrototype = self.prototypes[0]
        else:
            userProfileVector = self.users[userID].frequencyProfile

            distances = []
            for prototype in self.prototypes:
                distance = self.cosDistBetweenTwoSamples(userProfileVector, prototype.frequencyProfile)
                distances.append( (prototype, distance) )

            bestFit = min(distances,key= lambda t : t[1])
            self.users[userID].assignedPrototype = bestFit[0]
            bestFit[0].numberOfUsersAssigned += 1


    def evolve(self, userID, sequenceOfActions):
        if self.recursiveMode:
            self.evolveRecursively(userID, sequenceOfActions)
        else:
            self.evolveIteratively(userID, sequenceOfActions)
        self.evolutionCounter += 1

    def classifyAll(self):
        for prototype in self.prototypes:
            prototype.numberOfUsersAssigned = 0
        for user in self.users.keys():
            self.classifyProfile(user)

    def evolveIteratively(self, userID, sequenceOfActions):
        # this starts the show - algorithm runs
        self.addOrUpdateUser(userID, sequenceOfActions)
        P = self.calculateProfilePotentialIteratively(userID)
        self.users[userID].frequencyProfilePotential = P
        self.recalculatePrototypePotentials()
        if self.evaluateProfileForPrototype(P):
            self.evaluatePrototypesForRemovingAndRemove(userID)
            self.addPrototype(userID)
            # for user in self.users.keys():
                # self.classifyProfile(user)

    def evolveRecursively(self, userID, sequenceOfActions):
        self.addOrUpdateUserRecursively(userID, sequenceOfActions)
        P = self.updateProfilePotentialRecursively(userID)
        self.users[userID].frequencyProfilePotential = P
        self.calculateRecursiveSigmas(userID)
        self.recalculatePrototypePotentialsRecursively()
        if self.evaluateProfileForPrototype(P):
            self.evaluatePrototypesForRemovingAndRemove(userID)
            self.addPrototype(userID)
            # TODO: after recursive formula for sigma, you can remove this
        # elif userID not in [x.originalUser for x in self.prototypes]:
        #     del self.users[userID].frequencyProfile
            # for user in self.users.keys():
                # self.classifyProfile(user)

    def __str__(self):
        s = '--- EVABCD Classifier ---\nNumber of prototypes: %d\n' \
            'Number of users: %d\nEvolutions: %d\n' \
            'Total prototypes created: %d\n' % (
            len(self.prototypes), len(self.users), self.evolutionCounter, self.prototypeIDcounter
        )
        s+='Subsequence length: %d\n' % self.subsequenceLength

        s += '\nPrototypes:\n'
        for prototype in self.prototypes:
            s += '\t' + str(prototype) + '\n'

        u = True
        if u:
            s += '\nUsers:\n'
            for user in self.users.values():
                s += '\t' + str(user) + '\n'

        return s

    def writeReport(self, filename):
        with open(filename, 'w', encoding='utf-8') as file:

            s = '-------- EVABCD Classifier --------\nNumber of prototypes: %d\n' \
            'Number of users: %d\nEvolutions: %d\n' \
            'Total prototypes created: %d\n' % (
            len(self.prototypes), len(self.users), self.evolutionCounter, self.prototypeIDcounter
            )
            s+='Subsequence length: %d\n' % self.subsequenceLength
            s+= 35*'-'

            s += '\nPrototypes:\n\n'+ 71*'-' +'\nPrototype ID | based on user ID | potential | Users in class | sequence\n' + 71*'-' + '\n'
            file.write(s)
            for prototype in self.prototypes:
                s = ('%d | %d | %f | %d | %s' % (
                    prototype.id, prototype.originalUser, prototype.frequencyProfilePotential, prototype.numberOfUsersAssigned,
                    ';'.join(['%s : %f' % (k, v) for k, v in prototype.frequencyProfile.items() if v > 0])
                )) + '\n'
                file.write(s)

