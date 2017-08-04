# -*- coding: utf-8 -*-

import json
import codecs
from collections import OrderedDict

output = []
ref = codecs.open('disease_symptom.json', 'r', 'utf-8')
organFile = codecs.open('organ.txt', 'r', 'utf-8')
temp = organFile.readlines()
organList = []
for ele in temp:
    organList.append(ele.strip('\n').rstrip())
    
# Each line is a disease
for line in ref:
    data = {}
    curr = json.loads(line)
    data["id"] = curr.get("id")
    data["name"] = curr.get("name")
    
    # sym is a dictionay whose key is the symptom and value is the 
    # probability
    sym = curr.get("symptoms")
    symKeys = sym.keys()
    organDict = {}
    times = {}
    for eachKey in symKeys:
        for eachOrgan in organList:
            if eachKey.find(eachOrgan) != -1:
                if not eachOrgan in organDict:
                    organDict[eachOrgan] = sym.get(eachKey)
                    times[eachOrgan] = 1
                else:
                    organDict[eachOrgan] = organDict.get(eachOrgan) + sym.get(eachKey)
                    times[eachOrgan] = times.get(eachOrgan) + 1
    for ele in organDict:
        organDict[ele] = organDict.get(ele) / float(times.get(ele))

    data["organ"] = organDict
    ordered = OrderedDict(sorted(data.items(), key = lambda t:t[0]))

    output.append(ordered)

with open('disease_organ.json', 'w') as f:
    json.dump(output, f, ensure_ascii=False)
