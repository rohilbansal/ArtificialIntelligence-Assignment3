###################################
# CS B551 Fall 2016, Assignment #3
#
# Your names and user ids:
#
# (Based on skeleton code by D. Crandall)
#
#
####
# Put your report here!!
####

import random
import math
import time
from time import sleep
from collections import OrderedDict

# We've set up a suggested code structure, but feel free to change it. Just
# make sure your code still works with the label.py and pos_scorer.py code
# that we've supplied.
#
class Solver:
    def __init__(self):
        self.initialProbDict = {}
        self.transitionProbDict = {}
        self.emissionProbDict = {}
        self.countWordsDict = {}
        self.countPosDict = {}
        self.mostPosDict = {}
        self.viterbiStateDict = {}
        self.mostLikelyStateSeqDict = {}
        self.mostLikelyPOSList = []
        self.complexTransitionProb={}
        self.transitDict={}
        self.mostLikelyStateSeqCompDict={}
    # Calculate the log of the posterior probability of a given sentence
    #  with a given part-of-speech labeling
    def posterior(self, sentence, label):
        return 0

    # Do the training!
    def train(self, data):
        for item in data:
            #if element not in dict, count is 1, else fetch the value and increment the count
            #to do : divide
            #count the observed vars
            tupleWords = item[0]
            tuplePos = item[1]
            #print tupleWords
            for i in range(0,len(tupleWords)):
                if tupleWords[i] not in self.countWordsDict:
                    self.countWordsDict[tupleWords[i]] = 1
                else:
                    self.countWordsDict[tupleWords[i]] = self.countWordsDict[tupleWords[i]] + 1

                if tuplePos[i] not in self.countPosDict:
                    self.countPosDict[tuplePos[i]] = 1
                else:
                    self.countPosDict[tuplePos[i]] = self.countPosDict[tuplePos[i]] + 1

            if item[1][0] not in self.initialProbDict:
                self.initialProbDict[item[1][0]] = 1
            else:
                self.initialProbDict[item[1][0]] = self.initialProbDict[item[1][0]] + 1
            for i in range(0, len(item[1])):
                if i<len(item[1])-1: #else index out of range
                    if (item[1][i+1],item[1][i]) not in self.transitionProbDict:
                        self.transitionProbDict[(item[1][i+1],item[1][i])] = 1
                    else:
                        self.transitionProbDict[(item[1][i+1],item[1][i])] = self.transitionProbDict[(item[1][i+1],item[1][i])] + 1
                    
                if (item[0][i],item[1][i]) not in self.emissionProbDict: # check both elements of the tuple
                    self.emissionProbDict[(item[0][i],item[1][i])] = 1
                else:
                    self.emissionProbDict[(item[0][i],item[1][i])] = self.emissionProbDict[(item[0][i],item[1][i])] + 1

            for i in range(2,len(item[1])):
                if i<len(item[1])-2:
                    if (item[1][i+2],item[1][i+1]+'/'+item[1][i]) not in self.complexTransitionProb:
                        self.complexTransitionProb[(item[1][i+2],item[1][i+1]+'/'+item[1][i])] = 0.000001
                    else:
                        self.complexTransitionProb[(item[1][i+2],item[1][i+1]+'/'+item[1][i])] = self.complexTransitionProb[(item[1][i+2],item[1][i+1]+'/'+item[1][i])] + 1


        sumInitialProb = sum(self.initialProbDict.values())
        self.initialProbDict.update({n: float( self.initialProbDict[n])/ float(sumInitialProb)for n in self.initialProbDict.keys()})

        self.updateTransitions(self.transitionProbDict)
        self.updateTransitions(self.complexTransitionProb)
        listKeys = self.emissionProbDict.keys()
        for key in listKeys:
            self.emissionProbDict[key] = float(self.emissionProbDict[key])/float(self.countPosDict[key[1]])
        pass

    #function to update the transition probabilities of one-oreder model and two-order model

    def updateTransitions(self,dict):
        for key_1,value_1 in dict.items():
            den_sum = 0
            for key_2,value_2 in dict.items():
                if key_1[0] == key_2[0]:
                    den_sum = float(den_sum) + float(value_2)
            dict[key_1] = float(value_1) / float(den_sum)


    # Functions for each algorithm.
    #
    def simplified(self, sentence):
        mostPosDict=self.mostPosDict
        for i in range(0,len(sentence)):
            maxprob=0;
            if sentence[i] not in self.countWordsDict.keys():
                self.countWordsDict[sentence[i]]=0.000001
            for j in self.countPosDict:
                dictKey=(sentence[i],j) #changed to tuple
                if dictKey in self.emissionProbDict.keys():
                    currentprob = float(self.emissionProbDict[dictKey]) * float(self.countPosDict[j])/float(self.countWordsDict[sentence[i]])
                else:
                    currentprob = 0.000001
                if maxprob < currentprob:
                    maxprob = currentprob
                    mostPosDict[sentence[i]] = j+'@'+str(maxprob)

        return [[ [mostPosDict[sentence[i]].split('@')[0] for i in range(len(sentence))]], [ ['%.2f'%(float(mostPosDict[sentence[i]].split('@')[1])) for i in range(len(sentence))], ]]

    def returnMax(self,j,listPOS,emissionProb):
        maxProb = 0
        path = ''

        for i in listPOS:
            if (i,j) not in self.transitionProbDict:
                self.transitionProbDict[(i,j)] = 0.000001
            # print self.viterbiStateDict
            prob = self.viterbiStateDict[i] * self.transitionProbDict[(i,j)]
            if prob > maxProb:
                maxProb = prob
                path = i
        self.mostLikelyStateSeqDict[j] = maxProb*emissionProb

        return maxProb
    
    def hmm(self, sentence):
        #print("transition prob dict", self.transitionProbDict)
        self.mostLikelyPOSList = [] #empty it for each sentence
        listPOS = list(set(self.initialProbDict.keys()))

        for i in range(0,len(sentence)):
            for j in range(0,len(listPOS)):
                if (sentence[i],listPOS[j]) not in self.emissionProbDict:
                    self.emissionProbDict[(sentence[i],listPOS[j])] = 0.000001
                emissionProb = self.emissionProbDict[(sentence[i],listPOS[j])]
                if i==0:
                    #formula is initialProb*emissionProb
                    self.viterbiStateDict[listPOS[j]] = self.initialProbDict[listPOS[j]]*emissionProb 
                    self.mostLikelyStateSeqDict[listPOS[j]] = self.initialProbDict[listPOS[j]]*emissionProb   
                else:
                    #formula changed
                    maxValue = self.returnMax(listPOS[j],listPOS,emissionProb)
                    self.viterbiStateDict[listPOS[j]] =  maxValue * emissionProb
            #pick the maximum probable POS from the dict
            key, _ = max(self.mostLikelyStateSeqDict.iteritems(), key=lambda x:x[1])
            self.mostLikelyPOSList.append(key)
            self.mostLikelyStateSeqDict = {}
        return [[[self.mostLikelyPOSList[n] for n in range(len(sentence))]], []]

    def returncomplexmax(self,m,n,listPOS,ep):
        max_val=0

        for l in range(len(listPOS)):
            try:
                self.complexTransitionProb[(listPOS[l], listPOS[m] + '/' + listPOS[n])]
            except KeyError:
                self.complexTransitionProb[(listPOS[l], listPOS[m] + '/' + listPOS[n])] = 0.000001

            prob = math.log1p(self.transitDict[(listPOS[l],listPOS[m])] * self.complexTransitionProb[(listPOS[l],listPOS[m]+'/'+listPOS[n])])
            if prob > max_val:
                max_val = prob
            self.mostLikelyStateSeqCompDict[listPOS[n]] = max_val * ep
        return max_val

    def complex(self, sentence):
        mostlikelyPOS = []
        mostlikelyPOSProb=[]
        listPOS = list(set(self.initialProbDict.keys()))
        for i in range(len(sentence)):
            for j in range(len(listPOS)):
                self.transitDict[listPOS[j]] = math.log1p(self.initialProbDict[listPOS[j]] * \
                                               self.emissionProbDict[(sentence[i],listPOS[j])])

                for k in range(len(listPOS)):
                    self.transitDict[(listPOS[j],listPOS[k])] = math.log1p(self.transitDict[listPOS[j]] * self.transitionProbDict[(listPOS[j],listPOS[k])] * self.emissionProbDict[(sentence[i],listPOS[k])])
                    self.mostLikelyStateSeqCompDict[listPOS[k]] = self.transitDict[(listPOS[j],listPOS[k])]
        for i in range(len(sentence)):
            # self.mostLikelyStateSeqCompDict = {}
            for m in range(len(listPOS)):
                for n in range(len(listPOS)):
                    self.transitDict[(listPOS[m],listPOS[n])] = math.log1p(self.returncomplexmax(m,n,listPOS,self.emissionProbDict[(sentence[i],listPOS[n])]) * self.emissionProbDict[(sentence[i],listPOS[n])])
            d_descending = OrderedDict(sorted(self.mostLikelyStateSeqCompDict.items(),
                                                  key=lambda kv: kv[1], reverse=True))
            mostlikelyPOS.append(d_descending.keys()[0])
            mostlikelyPOSProb.append(d_descending[d_descending.keys()[0]])

        return [[[n for n in mostlikelyPOS]], [['%.2f' % (abs(math.log(n)) / 1000) for n in mostlikelyPOSProb], ]]

    # This solve() method is called by label.py, so you should keep the interface the
    #  same, but you can change the code itself. 
    # It's supposed to return a list with two elements:
    #
    #  - The first element is a list of part-of-speech labelings of the sentence.
    #    Each of these is a list, one part of speech per word of the sentence.
    #
    #  - The second element is a list of probabilities, one per word. This is
    #    only needed for simplified() and complex() and is the marginal probability for each word.
    #
    def solve(self, algo, sentence):
        if algo == "Simplified":
            return self.simplified(sentence)
        elif algo == "HMM":
            return self.hmm(sentence)
        elif algo == "Complex":
            return self.complex(sentence)
        else:
            print "Unknown algo!"

