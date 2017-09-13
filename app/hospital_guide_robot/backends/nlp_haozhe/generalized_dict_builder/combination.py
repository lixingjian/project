# -*- coding: utf-8 -*-

import codecs
import ahocorasick


ac = ahocorasick.Automaton()

# Get problem words
disable = set([])
appear = set([])
lack = set([])
bad = set([])
problem = []
prob_file = codecs.open('problem', 'r', 'utf-8')
for line in prob_file.readlines():
    line = line.rstrip()
    if line.startswith('S_disable'):
        words = line.split()
        for i in range(1, len(words)):
            disable.add(words[i])
            problem.append(words[i])
    elif line.startswith('S_appear'):
        words = line.split()
        for i in range(1, len(words)):
            appear.add(words[i])
            problem.append(words[i])
    elif line.startswith('S_lack'):
        words = line.split()
        for i in range(1, len(words)):
            lack.add(words[i])
            problem.append(words[i])
    elif line.startswith('S_bad'):
        words = line.split()
        for i in range(1, len(words)):
            bad.add(words[i])
            problem.append(words[i])
    else:
        problem.append(line)
#print('problem len is %d' % len(problem))

# Get the function words
function = []
func_file = codecs.open('function', 'r', 'utf-8')
for line in func_file.readlines():
    line = line.rstrip()
    function.append(line)

#print('function len is %d' % len(function))

# Get the organ words
organ = []
organ_file = codecs.open('organ', 'r', 'utf-8')
for line in organ_file.readlines():
    line = line.rstrip()
    organ.append(line)

#print('organ len is %d' % len(organ))

# Get the tissue words
tissue = []
tissue_file = codecs.open('tissue', 'r','utf-8')
for line in tissue_file.readlines():
    line = line.rstrip()
    tissue.append(line)

#print('tissue len is %d' % len(tissue))

# Get the indicator words
indicator = []
indicator_file = codecs.open('indicator', 'r', 'utf-8')
for line in indicator_file.readlines():
    line = line.rstrip()
    indicator.append(line)

# Get the nutrition words
nutrition = [] 
nutrition_file = codecs.open('nutrition', 'r', 'utf-8')
for line in nutrition_file.readlines():
    line = line.rstrip()
    nutrition.append(line)

#print('indicator len is %d' % len(indicator))


# Get the appearance words
appearance = []
appearance_file = codecs.open('appearance', 'r', 'utf-8')
for line in appearance_file.readlines():
    line = line.rstrip()
    appearance.append(line)

# Obtain the combinations
# Appearance 
new_word = set([])
for i in range(len(problem)):
    for j in range(len(function)):
        w1 = problem[i] + function[j]
        w2 = function[j] + problem[i]
        ac.add_word(w1, (len(ac), w1))
        ac.add_word(w2, (len(ac), w2))

#print('new_word len after p + f is %d ' % len(new_word))

for i in range(len(problem)):
    for j in range(len(organ)):
        w1 = problem[i] + organ[j]
        w2 = organ[j] + problem[i]
        ac.add_word(w1, (len(ac), w1))
        ac.add_word(w2, (len(ac), w2))
        

#print('new_word len after p + o is %d ' % len(new_word))

for i in range(len(problem)):
    for j in range(len(tissue)):
        w1 = problem[i] + tissue[j]
        w2 = tissue[j] + problem[i]
        ac.add_word(w1, (len(ac), w1))
        ac.add_word(w2, (len(ac), w2))

#print('new_word len after p + t is %d ' % len(new_word))

for i in range(len(problem)):
    for j in range(len(organ)):
        for k in range(len(tissue)):
            w1 = problem[i] + organ[j] + tissue[k]
            w2 = organ[j] + tissue[k] + problem[i]
            ac.add_word(w1, (len(ac), w1))
            ac.add_word(w2, (len(ac), w2))

#print('new_word len after p + o + t is %d ' % len(new_word))

for i in range(len(problem)):
    for j in range(len(indicator)):
        w1 = problem[i] + indicator[j]
        w2 = indicator[j] + problem[i]
        ac.add_word(w1, (len(ac), w1))
        ac.add_word(w2, (len(ac), w2))

#print('new_word len after p + i is %d ' % len(new_word))

for i in range(len(problem)):
    for j in range(len(nutrition)):
        w1 = problem[i] + nutrition[j]
        w2 = nutrition[j] + problem[i]
        ac.add_word(w1, (len(ac), w1))
        ac.add_word(w2, (len(ac), w2))

for i in range(len(problem)):
    for j in range(len(appearance)):
        w1 = problem[i] + appearance[j]
        w2 = appearance[j] + problem[i]
        ac.add_word(w1, (len(ac), w1))
        ac.add_word(w2, (len(ac), w2))

# Obtain to_check
to_check = set([])
check_file = codecs.open('to_check', 'r', 'utf-8')
for line in check_file.readlines():
    line = line.rstrip()
    to_check.add(line)

#print('to_check len is %d' % len(to_check))

ac.make_automaton()

# Obtain haodf input
haodf_file = codecs.open('haodf_longlong', 'r', 'utf-8')
xywy_file = codecs.open('xywy_longlong', 'r', 'utf-8')
res = {}
for line in haodf_file.readlines():
    try:
        content = line.split()[0]
    except:
        continue
    for end_index, symptom in ac.iter(content):
        sym = symptom[1]
        if sym in res:
            res[sym] += 1
        else:
            res[sym] = 1

for line in xywy_file.readlines():
    for end_index, symptom in ac.iter(line):
        sym = symptom[1]
        if sym in res:
            res[sym] += 1
        else:
            res[sym] = 1

after_sort = sorted(res.items(), key=lambda x: x[1], reverse = True)

for ele in after_sort:
    print(ele)

