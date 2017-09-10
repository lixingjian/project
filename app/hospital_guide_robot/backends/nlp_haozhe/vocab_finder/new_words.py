# -*- coding: utf-8 -*-
import codecs
import numpy
from numpy import matrix
import sys
import time

def count_times(in_file_name):
    times = {}
    in_file = codecs.open(in_file_name, 'r', 'utf-8')
    for line in in_file.readlines():
        words = line.rstrip().split()
        for ele in words:
            if not ele in times:
                times[ele] = 1
            else:
                times[ele] += 1
    after_sort = sorted(times.items(), key=lambda x: x[1], reverse = True)
    return (times, after_sort)

def assign_id(after_sort):
    word_to_id = {}   # key is word, value is id
    id_to_word = {}   # key is id, value is word
    i = 0
    for ele in after_sort:
        word_to_id[ele] = i
        id_to_word[i] = ele
        i += 1

    return (word_to_id, id_to_word)

def count_total(times):
    total = 0
    for ele in times.values():
        total += ele
    return total

"""
def get_curr(times, curr):
    for ele in times:
        if ele[0] == curr:
            return ele[1]
    return -1
"""

def construct_matrix(times, after_sort, word_to_id, id_to_word, in_file_name):
    size = min(len(after_sort), 20000)
    matrix = numpy.zeros((size, size))
    total = count_total(times)
    for i in range(size):
        curr = id_to_word.get(i)
        num = times.get(curr)
        #num = get_curr(times, curr)
        matrix[i][i] = num / total

    in_file = codecs.open(in_file_name, 'r', 'utf-8')
    combination_times = 0
    for line in in_file.readlines():
        words = line.rstrip().split()
        for i in range(len(words) - 1):
            w1 = words[i]
            w2 = words[i + 1]
            id1 = word_to_id.get(w1)
            id2 = word_to_id.get(w2)

            if id1 >= size or id2 >= size:
                continue
            # Uncomment the lines below to ommit half of the matrix
            # However, the order of the words will be messed up
            """
            if id1 < id2:
                matrix[id1][id2] += 1
            else:
                matrix[id2][id1] += 1
            """
            matrix[id1][id2] += 1
            combination_times += 1

    for i in range(size):
        for j in range(size):
            #if i < j:
                # matrix[i][j] = matrix[i][j] / (total * total)
            if i != j:
                matrix[i][j] = matrix[i][j] / combination_times

    return matrix

def analyze_matrix(matrix, id_to_word, in_file_name): 
    #print('now analyzing the matrix')
    result = set([])
    for i in range(matrix.shape[0]):
        for j in range(matrix.shape[0]):
            #if i < j and matrix[i][j] != 0:
            if i != j and matrix[i][j] != 0:
                product = matrix[i][i] * matrix[j][j]
                div =  product / matrix[i][j]
                #print('word is ' + id_to_word.get(i) + id_to_word.get(j))
                #print('div is ' + str(div))
                #print('product is ' + str(product))
                #print('matrix value is ' + str(matrix[i][j]))
                #print()
                if div < 0.001:
                    temp_res = check_left(matrix, id_to_word, i, j, in_file_name)
                    for each in temp_res:
                        ratio = find_ratio(each[0], each[1], in_file_name)
                        if ratio < 0.7:
                            continue
                        if not (each[0], each[1]) in result:
                            result.add((each[0], each[1]))

                    temp_res = check_right(matrix, id_to_word, i, j, in_file_name)
                    for each in temp_res:
                        ratio = find_ratio(each[0], each[1], in_file_name)
                        if ratio < 0.7:
                            continue
                        if not (each[0], each[1]) in result:
                            result.add((each[0], each[1]))
                    
                    #result.append((id_to_word.get(i), id_to_word.get(j)))
    
    return result

def check_left(matrix, id_to_word, id1, id2, in_file_name):
    in_file = codecs.open(in_file_name, 'r', 'utf-8')
    w1 = id_to_word.get(id1)
    w2 = id_to_word.get(id2)
    count = {}
    result = set([])
    for line in in_file.readlines():
        words = line.rstrip().split()
        for i in range(1, len(words) - 1):
            if words[i] == w1 and words[ i + 1] == w2:
                curr = words[i - 1]
                if not curr in count:
                    count[curr] = 0
                else:
                    count[curr] += 1

    for key, val in count.items():
       if val / matrix[id1][id2] > 0.2:
            result.add((key, w1 + w2))

    if len(result) == 0:
        result.add((w1, w2))

    return result

def check_right(matrix, id_to_word, id1, id2, in_file_name):
    in_file = codecs.open(in_file_name, 'r', 'utf-8')
    w1 = id_to_word.get(id1)
    w2 = id_to_word.get(id2)
    count = {}
    result = set([])
    for line in in_file.readlines():
        words = line.rstrip().split()
        for i in range(1, len(words) - 1):
            if words[i - 1] == w1 and words[i] == w2:
                curr = words[i + 1]
                if not curr in count:
                    count[curr] = 0
                else:
                    count[curr] += 1
    for key, val in count.items():
        if val / matrix[id1][id2] > 0.2:
            result.add((key, w1 + w2))

    if len(result) == 0:
        result.add((w1, w2))

    return result

def find_ratio(w1, w2, in_file_name):
    in_file = codecs.open(in_file_name, 'r', 'utf-8')
    both = 0
    adjacent = 0

    for line in in_file.readlines():
        if line.find(w1) >= 0 and line.find(w2) >= 0:
            both += 1
            if line.find(w1) == line.find(w2) + len(w2) + 1:
                adjacent += 1
            elif line.find(w2) == line.find(w1) + len(w1) + 1:
                adjacent += 1
    
    if both == 0:
        return 0

    ratio = adjacent / both

    return ratio

def main(in_file_name):
    temp = count_times(in_file_name)
    times = temp[0]
    after_sort = temp[1]
    dicts = assign_id(times)
    word_to_id = dicts[0]
    id_to_word = dicts[1]
    matrix = construct_matrix(times, after_sort, word_to_id, id_to_word, in_file_name)
    #for i in range(len(times)):
        #print(dicts[1][i], end = '\t')
    #print()
    #print(matrix)
    #print(matrix[len(times) - 1][len(times) - 1])

    result = analyze_matrix(matrix, id_to_word, in_file_name)
    #print(result)
    for w1, w2 in result:
        print(w1 + w2)

if __name__ == '__main__':
    start_time = time.time()
    main(sys.argv[1])
    sys.stderr.write("--- %s seconds ---\n" % (time.time() - start_time))
    """
    res = count_times('haodf_long_ltp')

    for i in range(len(res)):
        if i < 20000:
            print(res[i][0] + '\t' + str(res[i][1]))
        #else:
            #print('extra ' + res[i][0] + '\t' + str(res[i][1]))

    """

