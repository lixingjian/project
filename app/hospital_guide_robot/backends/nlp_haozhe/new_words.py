# -*- coding: utf-8 -*-
import codecs
import numpy
from numpy import matrix

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

    return times

def assign_id(times):
    word_to_id = {}   # key is word, value is id
    id_to_word = {}   # key is id, value is word
    i = 0
    for ele in times.keys():
        word_to_id[ele] = i
        id_to_word[i] = ele
        i += 1

    return (word_to_id, id_to_word)

def count_total(times):
    total = 0
    for key, val in times.items():
        total += val
    return total

def construct_matrix(times, word_to_id, id_to_word, in_file_name):
    size = count_total(times)
    matrix = numpy.zeros((size, size))
    total = count_total(times)
    for i in range(len(times)):
        curr = id_to_word.get(i)
        num = times.get(curr)
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

    for i in range(len(times)):
        for j in range(len(times)):
            #if i < j:
                # matrix[i][j] = matrix[i][j] / (total * total)
            if i != j:
                matrix[i][j] = matrix[i][j] / combination_times

    return matrix

def analyze_matrix(matrix, id_to_word, in_file_name): 
    print('now analyzing the matrix')
    result = []
    for i in range(len(id_to_word)):
        for j in range(len(id_to_word)):
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
                        if not (each[0], each[1]) in result:
                            result.append((each[0], each[1]))

                    temp_res = check_right(matrix, id_to_word, i, j, in_file_name)
                    for each in temp_res:
                        if not (each[0], each[1]) in result:
                            result.append((each[0], each[1]))
                    
                    #result.append((id_to_word.get(i), id_to_word.get(j)))
    return result

def check_left(matrix, id_to_word, id1, id2, in_file_name):
    in_file = codecs.open(in_file_name, 'r', 'utf-8')
    w1 = id_to_word.get(id1)
    w2 = id_to_word.get(id2)
    count = {}
    result = []
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
            result.append((key, w1 + w2))

    if len(result) == 0:
        result.append((w1, w2))

    return result

def check_right(matrix, id_to_word, id1, id2, in_file_name):
    in_file = codecs.open(in_file_name, 'r', 'utf-8')
    w1 = id_to_word.get(id1)
    w2 = id_to_word.get(id2)
    count = {}
    result = []
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
            result.append((key, w1 + w2))

    if len(result) == 0:
        result.append((w1, w2))

    return result


def main():
    #in_file_name = './find_new_in/2_in'
    in_file_name = 'short_in'
    times = count_times(in_file_name)
    #for key, val in times.items():
        #print(key + ' ' + str(val))
    dicts = assign_id(times)
    word_to_id = dicts[0]
    id_to_word = dicts[1]
    matrix = construct_matrix(times, word_to_id, id_to_word, in_file_name)
    #for i in range(len(times)):
        #print(dicts[1][i], end = '\t')
    print()
    print(matrix)
    #print(matrix[len(times) - 1][len(times) - 1])

    result = analyze_matrix(matrix, id_to_word, in_file_name)
    print(result)
    for w1, w2 in result:
        print(w1 + w2)

if __name__ == '__main__':
    main()
