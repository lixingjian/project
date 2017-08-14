# -*- coding: utf-8 -*-

"""
Created: Aug 1, 2017
Author: Haozhe

This file extacts the keywords from a patient's description and prints
out the corresponding expressions stored in our dictionary

Update(Aug 9, 2017) Improvement made to reduce duplicated chars

NOTE: Use Python 3.5 to run
"""

import ahocorasick
import json
import codecs

class Match:
    def __init__(self):
        self.ac = ahocorasick.Automaton()
        self.synAc = ahocorasick.Automaton()

    def load(self, fileName, organFile, commonFile, feelingFile):
        # Take in disease symptoms, names and related organs 
        result = []
        # Read the file in utf-8 to display Chinese characters
        inputData = codecs.open (fileName, 'r', 'utf-8')
        organData = codecs.open(organFile, 'r', 'utf-8')
        commonData = codecs.open(commonFile, 'r', 'utf-8')
        feelingData = codecs.open(feelingFile, 'r', 'utf-8')
        for line in inputData:
            currContent = json.loads(line)
            sym = currContent.get("symptoms")
            tuples = sym.items()
            for eachTuple in tuples:
                if not eachTuple[0] in result:
                    result.append(eachTuple[0])
                    self.ac.add_word(eachTuple[0], (len(self.ac),eachTuple[0]))
            disease = currContent.get("name")
            self.ac.add_word(disease, (len(self.ac),disease))

        for line in organData:
            curr = json.loads(line)
            organ = curr.get("organ")
            for eachTuple in organ.items():
                if not eachTuple[0] in result:
                    result.append(eachTuple[0])
                    self.ac.add_word(eachTuple[0], (len(self.ac),eachTuple[0]))

        for line in commonData:
            sym_list = line.split(' ')[0].split(',')
            for ele in sym_list:
                self.ac.add_word(ele, (len(self.ac),ele))

        for line in feelingData:
            self.ac.add_word(line.rstrip(), (len(self.ac),line.rstrip()))
    
    def match(self, description, synFileName, sympFileName):
        # Process the description, removing adverbs and punctuations
        advFile = codecs.open ('Adverbs.json', 'r', 'utf-8')
        adv = json.load(advFile)
        for eachAdv in adv:
            description = description.replace(eachAdv, "")
        for punc in ["，","。","？","！", "、"," "]:
            description = description.replace(punc, "")

        synDict = self.createSynDict(synFileName,sympFileName)
        description = self.replaceSyn(description, synDict)
    
        # ac_match takes place here
        self.ac.make_automaton()
        result = []
        for end_index, symptom in self.ac.iter(description):
            sym = symptom[1]
            if not sym in result:
                result.append(sym)
        copy = []
        for each in result:
            copy.append(each)

        for ele in result:
            for other in result:
                if ele == other:
                    continue
                if ele.find(other) >= 0 and other in copy:
                    copy.remove(other)
                else: 
                    continue

        # Return a string format 
        return ''.join((str(x) + ' ') for x in copy)

    def combine(self, string, organFile, feelingFile):
        organList = []
        feelingList =[]
        for line in open(organFile).readlines():
            organList.append(line.rstrip())
        for line in open(feelingFile).readlines():
            feelingList.append(line.rstrip())
        
        temp = []
        word = string.split()
        for i in range(len(word) - 1):
            if word[i] in organList and word[i+1] in feelingList:
                temp.append(word[i] + word[i+1])
            
        result = string.split()
        for each in word:
            for i in range(len(temp)):
                if temp[i].find(each) >= 0:
                    result.remove(each)
                    if temp[i] not in result:
                        result.append(temp[i])

        return ''.join((str(x) + ' ') for x in result)

    # Helper method which is used in createSynDict()
    def wordInSymp(self, wordString, sympList):
        word = wordString.split(',')
        toReturn = []
        for eachWord in word:
            if eachWord in sympList:
                toReturn.append(eachWord)
        return toReturn
        
    def createSynDict(self, synFileName, sympFileName):
        # First load the symptoms
        symptoms = []
        inputData = codecs.open(sympFileName, 'r', 'utf-8')
        for line in inputData:
            currContent = json.loads(line)
            sym = currContent.get("symptoms")
            for eachTuple in sym.items():
                if eachTuple[0] not in symptoms:
                    symptoms.append(eachTuple[0])
        # Finsh loading the symptoms in a list

        # Then load the synonyms from synFile
        synFile = codecs.open(synFileName, 'r', 'utf-8')
        tempList = synFile.readlines()
        synList = []
        for i in range(len(tempList)):
            synList.append(tempList[i].replace('\n', ''))
        
        # Create a dictionary whose key is a synonym of the symptom
        # and value is the symptom
        synDict = {}
        for i in range(len(synList)):
            currWord = self.wordInSymp(synList[i], symptoms)
            if len(currWord) == 0:
                pass
            else:
                splitted = synList[i].split(',')
                for word in splitted:
                    for j in range(len(currWord)):
                        if word == currWord[j]:
                            pass
                        else:
                            synDict[word] = currWord[j]
        return synDict

    def replaceSyn(self, description, synDict):
        # Load the trie structure first
        for key in synDict.keys():
            self.synAc.add_word(key, key)
        self.synAc.make_automaton()
        for end_index, syn in self.synAc.iter(description):
            description = description.replace(syn, synDict.get(syn))
        return description
        

        

if __name__ == '__main__':
        matcher = Match()
        matcher.load('disease_symptom.json', 'disease_organ.json', 'common.txt','feeling.txt')
        while 1:
            result = ''
            description = input(u'请输入症状描述: ')
            for eachPart in description.split('，'):
                temp = matcher.match(eachPart,'syn1.txt','disease_symptom.json')
                print('temp is ' + temp)
                res = matcher.combine(temp, 'organ.txt', 'feeling.txt')
                print('res is ' + res)
                result = result + res
            print(result)
