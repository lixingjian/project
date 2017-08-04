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
UNWANTED = ['内科','外科','普通内科','中医科','普内','普内科','儿科','五官科','普通外科','普外科','普外']

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


    count = 0
    i = 0
    d = Diagnosis()
    failed = 0
    # report to log discrepancies between prediction and actual results
    report = {}
    matched = {}

    # Process the natural language and extract keywords
    matcher = Match()
    matcher.load("disease_symptom.json", "disease_organ.json")

    # Modify the output of the model for better classification of departments
    deptSynFile = open('synDept.txt', 'r')
    deptSynDict = {}
    deptSynList = deptSynFile.readlines()
    for k in range(len(deptSynList)):
        tempList = deptSynList[k].strip('\n').split(',')
        for m in range(len(tempList)):
            deptSynDict[tempList[m]] = tempList[0]

    for describe in DES_list:
        # Extracting keywords takes place here
        original = describe.strip('\n')
        describe = matcher.match(describe, 'syn1.txt', 'disease_symptom.json').rstrip()
        req = {'user': {'sex': 1, 'age': 30}, 'cont': {'req_text': describe, 'req_type': 0, 'res_text': ''}}
        req_list = [req]
        response = d.run(json.dumps(req_list, ensure_ascii = False))
        if len(response) == 0:
            predictedDept = 'Failed due to no input'
            failed += 1
        else:
            predictedDept = response.split(' ')[0].rstrip()
            if predictedDept in UNWANTED:
                predictedDept = response.split(' ')[1].rstrip()

        if predictedDept in deptSynDict:
            predictedDept = deptSynDict.get(predictedDept)

        if DEP_list[i] in deptSynDict:
            DEP_list[i] = deptSynDict.get(DEP_list[i])

        if predictedDept == DEP_list[i]:
            count += 1
            matched[i + 1] = [original, describe, predictedDept, DEP_list[i]]
        else:
            report[i + 1] = [original, describe, predictedDept, DEP_list[i]]
        i+=1
    print (failed)
    percentage = (float(count)/float(len(DEP_list) - failed)) * HUNDRED
    accuracy = "Estimated accuracy: " + str(percentage) + "%"
    correct = "\n\nCorrect results: \n"
    incorrect = "\n\nIncorrect results: \n"
    
    outputFile = open ('test_result.txt', 'w')
    outputFile.write(accuracy + '\n' + correct)
    outputFile.write("".join('{}{}\n'.format(key, val) for key, val in sorted(matched.items())))
    outputFile.write(incorrect)
    outputFile.write("".join('{}{}\n'.format(key, val) for key, val in report.items()))

    outputFile.close()
    symFile.close()
    deptFile.close()

if __name__ == '__main__':
    main()
