# -*- coding: utf-8 -*-

import codecs
from Extractor import Extractor

def read_file():
    # Read the input file and create correct tuples
    f = codecs.open('input_nlp_test', 'r', 'utf-8')
    lines = f.readlines()
    return lines
"""
Tuple样例格式：
(['O_鼻部', 'O_头部'], [[], []], ['Tissue list is empty'], ['Indicator list is
empty'], ['F_疼痛'], ['时'], -1, ['Not_included list is empty'], -1, -1, -1,
'起因暂无', '加剧因素暂无', '缓解因素暂无', ['History list is empty'], ['Suspect
list is empty'], ['Eliminate list is empty'])
"""

#i = 0
#while i < len(lines):

def read_line_list(lines, i, increment, output):
    curr_str = lines[i + increment].rstrip()
    if curr_str == 'N':
        pass
    else:
        curr_temp = curr_str.split()
        for ele in curr_temp:
            output.append(ele)

def read_line_int(lines, i, increment, output):
    curr_str = lines[i + increment].rstrip()
    if curr_str =='N':
        pass
    else:
        output = int(curr_str)
    return output

def format_tuple(res, in_list, name):
    if len(in_list) == 0:
        res += ([ name + ' list is empty'],)
    else:
        res += (in_list,)
    return res

def get_one_set(lines):

    organs = []
    location = []
    tissue = []
    indicator = []
    problem = []
    form = []
    severity = -1
    not_included = []
    suddenness = -1
    frequency = -1
    time = -1
    trigger = '起因暂无'      # Not considered in this phase
    worsen = '加剧因素暂无'   # Not considered in this phase
    relief = '缓解因素暂无'   # Not considered in this phase
    history = []
    suspect = []
    eliminate = []
    one_set = []

    description = lines[i].rstrip()
    one_set.append(description)

    read_line_list(lines, i, 1, organs)

    location_str = lines[i + 2]
    location_temp = location_str.split()
    for ele in location_temp:
        if ele == 'N':
            location.append([])
        else:
            temp = ele.split('#')
            curr = []
            for each in temp:
                curr.append(each)
            location.append(curr)

    read_line_list(lines, i, 3, tissue)
    read_line_list(lines, i, 4, indicator)

    problem_str = lines[i + 5].rstrip()
    problem_temp = problem_str.split()
    num_of_tuple = len(problem_temp)

    read_line_list(lines, i, 6, form)
    severity = read_line_int(lines, i, 7, severity)
    read_line_list(lines, i, 8, not_included)
    suddenness = read_line_int(lines, i, 9, suddenness)
    frequency = read_line_int(lines, i, 10, frequency)
    time = read_line_int(lines, i, 11, time)
    read_line_list(lines, i, 15, history)
    read_line_list(lines, i, 16, suspect)
    read_line_list(lines, i ,17, eliminate)

            
    for j in range(num_of_tuple):
        res = ()
        res = format_tuple(res, organs, 'Organ')
        res = format_tuple(res, location, 'Location')
        res = format_tuple(res, tissue, 'Tissue')
        res = format_tuple(res, indicator, 'Indicator')
        problem = [problem_temp[j]]
        res = format_tuple(res, problem, 'Problem')
        res = format_tuple(res, form, 'Form')
        res +=  (severity,) 
        res = format_tuple(res, not_included, 'Not_included')
        res +=  (suddenness,) + (frequency,) + (time,)
        res +=  (trigger,) + (worsen,) + (relief,)
        res = format_tuple(res, history, 'History')
        res = format_tuple(res, suspect, 'Suspect')
        res = format_tuple(res, eliminate, 'Eliminate')
        one_set.append(res)
    return one_set

def get_all_content(list_of_lists):
    result = []
    for each_list in list_of_lists:
        for ele in each_list:
            result.add(ele)
    return result

def calculate_organ_part(correct, extract):
    total_score = 35.0
    curr_score = 0
    body = []
    body.append(correct[0][0])
    body.append(correct[0][2])
    body.append(correct[0][3])
    correct_body = get_all_content(body)

    body = []
    body.append(extract[0][0])
    body.append(extract[0][2])
    body.append(extract[0][3])
    extract_body = get_all_content(body)

    each_score = total_score / len(correct_body)
    for each in correct_body:
        if each in extract_body:
            curr_score += each_score
    return curr_score
    

# Main function starts here
i = 0
lines = read_file()
extractor = Extractor()
while i < len(lines):
    print ('Test No. ' + str(int(i / 18 + 1)))
    one_set = get_one_set(lines)
    result = extractor.extract(one_set[0])

    print('\nIdeal results are: ')
    for j in range(1, len(one_set)):
        print(one_set[j])
        print()

    print('\nExtracted results are: ')
    for each in result:
        print(each)
        print()

    organ_score = calculate_organ_part(one_set, result)
    print(organ_score)

    i += 18
    print('\n')
    extractor.reset()
