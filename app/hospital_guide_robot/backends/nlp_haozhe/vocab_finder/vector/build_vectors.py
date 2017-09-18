# -*- coding: utf-8 -*-
import codecs
import numpy as np
from sklearn import preprocessing
from sklearn.metrics.pairwise import cosine_similarity

# Get all candidates from problem_nlp
problem = set([])
check_file = codecs.open('../../problem_nlp', 'r', 'utf-8')
for line in check_file:
    curr = line.split()
    for ele in curr:
        if ele.find('#') >= 0:
            continue
        problem.add(ele)

print('Get problem set success.')

# Find names of each vector component and assign it an id
result_file = codecs.open('result/representation.xywypage', 'r', 'utf-8')
#result_file = codecs.open('result/short', 'r', 'utf-8')

vector_comp = {} # key is component name, val is id
vector_id = {} # key is id, val is component name
i = 0
lines = result_file.readlines()

# Find top 2000 vector_comp
count = {}
for line in lines:
    content = line.split()
    for k in range(1, len(content)):
        curr = content[k].split(':')
        try:
            name = curr[0]
            num = float(curr[1])
        except:
            continue
        if not name in count:
            count[name] = num
        else:
            count[name] += num

after_sort = sorted(count.items(), key=lambda x:x[1], reverse = True)
candidate = set([])
for j in range(min(2000, len(after_sort))):
    candidate.add(after_sort[j][0])

print('Get top 2000 success.')

for line in lines:
    content = line.split()
    for k in range(1, len(content)):
        curr = content[k].split(':')
        if curr[0] in candidate and not curr[0] in vector_comp:
            vector_comp[curr[0]] = i
            vector_id[i] = curr[0]
            i += 1

print('Get two dictionaries success.')

known_vectors = []
unknown_vectors = []
# Create known vectors and put corresponding content into them
for line in lines:
    vector = np.zeros(len(vector_comp))
    content = line.split()
    total = 0
    for k in range(1, len(content)):
        curr = content[k].split(':')
        try:
            name = curr[0]
            num = float(curr[1])
        except:
            continue
        if not name in candidate:
            continue
        total += num
        comp_id = vector_comp.get(name)
        vector[comp_id] = num

    # Normalize vector
    vector_normalized = preprocessing.normalize(vector.reshape(1,-1), norm='l2')

    if content[0] in problem:
        known_vectors.append(vector_normalized)
    else:
        unknown_vectors.append((vector_normalized, content[0]))

print('Get all vectors success.')

# Calculate the average of the knwon vectors
average_vector = np.zeros(len(vector_comp))
for i in range(len(vector_comp)):
    curr_sum = 0
    for each in known_vectors:
        curr_sum += each[0][i]
    average = curr_sum / max(len(known_vectors),1)
    average_vector[i] = average

# Normalize average _vector
average_normalized = preprocessing.normalize(average_vector.reshape(1,-1), norm='l2')

# Calculate cosine similarity of the normalized average vector and each unkonwn
# vector
for ele, word in unknown_vectors:
    sim = cosine_similarity(ele, average_normalized)
    if sim.item(0) > 0.8:
        print(sim.item(0))
        print(word)
        print()
