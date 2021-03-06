# -*- coding: utf-8 -*-

"""
Created: Aug 1, 2017
Author: Haozhe

This file extacts the keywords from a patient's description and prints
out the corresponding expressions stored in our dictionary

Update(Aug 2, 2017) Incorporated synonyms while extracting keywords
1. match() now must have 3 parameters
2. Include a txt file of synonyms while runniing the program

Update(Aug 3, 2017) Made some improvements
1. Fixed a bug in wordInSym()
2. Now the program can extract disease names from description

Update(Aug 4, 2017) Include the function to extract organ keywords

NOTE: Use Python 3.5 to run
"""

import ahocorasick
import json
import codecs

class Match:
    def __init__(self):
        self.ac = ahocorasick.Automaton()
        self.synAc = ahocorasick.Automaton()

    def load(self, fileName, organFile):
        # Take in disease symptoms, names and related organs 
        result = []
        # Read the file in utf-8 to display Chinese characters
        inputData = codecs.open (fileName, 'r', 'utf-8')
        organData = codecs.open(organFile, 'r', 'utf-8')
        for line in inputData:
            currContent = json.loads(line)
            sym = currContent.get("symptoms")
            tuples = sym.items()
            for eachTuple in tuples:
                if not eachTuple[0] in result:
                    result.append(eachTuple[0])
                    self.ac.add_word(eachTuple[0], eachTuple[0])
            disease = currContent.get("name")
            self.ac.add_word(disease, disease)
        curr = json.load(organData)
        for ele in curr:
            # ele is a dict
            organs = ele.get("organ")
            for eachTuple in organs.items():
                if not eachTuple[0] in result:
                    result.append(eachTuple[0])
                    self.ac.add_word(eachTuple[0], eachTuple[0])
    
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
            symptom = symptom + ' '
            if not symptom in result:
                result.append(symptom)
        # Return a string format 
        return ''.join(str(x) for x in result)

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
    matcher.load('disease_symptom.json', 'disease_organ.json')
    res = matcher.match(input(u'请输入症状描述: '),
    'syn1.txt','disease_symptom.json')
    print(res)
