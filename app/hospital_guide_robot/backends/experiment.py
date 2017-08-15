#-*- coding: utf-8 -*-
"""
Created on Tue Aug  1 09:39:44 2017

@author: Xie
"""

from Match import Match
from predict_disease import Diagnosis
import json

INDEX_OF_DEPT = 0
HUNDRED = 100
UNWANTED = ['内科','外科','普通内科','中医科','普内','普内科','儿科','五官科','疼痛科','急诊科']

def main():
    symFile = open ('symptom_input.txt', 'r')
    deptFile = open ('department_input.txt', 'r')

#    symFile = open ('smallsym.txt', 'r')
#    deptFile = open ('smalldept.txt', 'r')

    # Get the description of symptoms
    DES_list = symFile.readlines()
    print ("DES LEN: " + str(len(DES_list)))
   
    # Get the departments (correct results)
    read_list = deptFile.readlines()
    DEP_list = []
    for j in range(len(read_list)):
        DEP_list.append(read_list[j].strip('\n').rstrip())
    print ("DEP LEN: " + str(len(DEP_list)))

    matcher = Match()
    matcher.load("disease_symptom.json", "disease_organ.json", 'common.txt', 'feeling.txt')

    count = 0
    i = 0
    d = Diagnosis()
    failed = 0
    # report to log discrepancies between prediction and actual results
    report = {}
    matched = {}

    # Modify the output of the model for better classification of departments
    deptSynFile = open('synDept.txt', 'r')
    deptSynDict = {}
    deptSynList = deptSynFile.readlines()
    for k in range(len(deptSynList)):
        tempList = deptSynList[k].strip('\n').split(',')
        for m in range(len(tempList)):
            deptSynDict[tempList[m]] = tempList[0]

    for describe in DES_list:
        # Extracting keywords takes place in predict_disease.py
        original = describe.strip('\n')
        req = {'user': {'sex': 1, 'age': 30}, 'request': {'text': describe, 'type': 0}}
        description = matcher.match(req['request']['text'], 'syn1.txt', 'disease_symptom.json').rstrip()

        req_list = [req]
        for part in describe.split(' '):
            if part.startswith('age='):
                req['user']['age'] = int(part[len('age='):])
            if part.startswith('sex='):
                req['user']['sex'] = int(part[len('sex='):])
        prediction = d.run(req_list)
        predictedDept = prediction.get('text')
        candidates = prediction.get('candidates')
        if predictedDept == None or len(predictedDept) == 0:
            predictedDept = 'Failed due to no input'
            failed += 1
        
        # Modify the result predicted as specified in synDipt.txt
        if predictedDept in deptSynDict:
            predictedDept = deptSynDict.get(predictedDept)

        if DEP_list[i] in deptSynDict:
            DEP_list[i] = deptSynDict.get(DEP_list[i])

        if predictedDept == DEP_list[i]:
            count += 1
            matched[i + 1] = [original, description, candidates, predictedDept, DEP_list[i]]
        else:
            report[i + 1] = [original, description, candidates, predictedDept, DEP_list[i]]
        i+=1
        print(i)

    print('number of descriptions failed to find keywords')
    print (failed)    # Print the number of descriptions from which we failed to
                      # extract keywords
    percentage = (float(count)/float(len(DEP_list) - failed)) * HUNDRED
    overallPerc = float(count)/float(len(DEP_list)) * HUNDRED
    accuracy = "Estimated model accuracy: " + str(percentage) + "%"
    overallAccu = "Overall accuracy: " + str(overallPerc) + "%"
    correct = "\n\nCorrect results: \n"
    incorrect = "\n\nIncorrect results: \n"
    
    outputFile = open ('test_result.txt', 'w')
    outputFile.write(accuracy + '\n' + overallAccu + '\n' + correct)
    outputFile.write("".join('{}{}\n'.format(key, val) for key, val in sorted(matched.items())))
    outputFile.write(incorrect)
    outputFile.write("".join('{}{}\n'.format(key, val) for key, val in report.items()))

    outputFile.close()
    symFile.close()
    deptFile.close()

if __name__ == '__main__':
    main()
