# -*- coding: utf-8 -*-

import codecs
import statistics
from Extractor import Extractor

"""
Tuple样例格式：
(['O_鼻部', 'O_头部'], [[], []], ['Tissue list is empty'], ['Indicator list is
empty'], ['F_疼痛'], ['时'], -1, ['Not_included list is empty'], -1, -1, -1,
'起因暂无', '加剧因素暂无', '缓解因素暂无', ['History list is empty'], ['Suspect
list is empty'], ['Eliminate list is empty'])
"""

def read_file():
    # Read the input file and create correct tuples
    f = codecs.open('input_nlp_test', 'r', 'utf-8')
    lines = f.readlines()
    return lines

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
    #if len(in_list) == 0:
    #    res += ([ name + ' list is empty'],)
    #else:
    #    res += (in_list,)
    res += (in_list,)
    return res

def get_one_set(lines):
    
    # This method will output the tuples of one description
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

    # Formatting the output tuple (for debugging purposes)        
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
        if len(each_list) == 0:
            continue
        for ele in each_list:
            result.append(ele)
    return result

def calculate_organ_part(correct, extract):
    total_score = 30.0
    curr_score = 0.0
    body = []
    body.append(correct[1][0])
    body.append(correct[1][2])
    body.append(correct[1][3])
    correct_body = get_all_content(body)

    body = []
    body.append(extract[0][0])
    body.append(extract[0][2])
    body.append(extract[0][3])
    extract_body = get_all_content(body)

    # If there is nothing, get all points (35)
    if len(correct_body) == 0:
        curr_score = total_score
        return curr_score

    # Each extra item in extract result will lead to deduction of 5 points
    if len(extract_body) > len(correct_body):
        diff = len(extract_body) - len(correct_body)
        curr_score -= 5 * diff

    for i in range(len(extract_body)):
        extract_body[i] = extract_body[i].split('_')[-1]

    #print('correct ones are: ' + str(correct_body))
    #print('extracted ones are: ' + str(extract_body))

    # Each item has score 35/(num of items)
    each_score = total_score / len(correct_body)
    for each in correct_body:
        if each in extract_body:
            curr_score += each_score
    return curr_score

def calculate_symp_part(correct, extract):
    symp_score = 30.0
    form_score = 5.0
    curr_score = 0.0
    
    correct_prob = []
    extract_prob = []
    # First compare problem list only
    for i in range(1, len(correct)):
        correct_prob.append(correct[i][4][0])
    for i in range(len(extract)):
        if len(extract[i][4]) == 0:
            extract_prob.append('')
        else:
            extract_prob.append(extract[i][4][0].split('_')[-1])
    
    # Each extra item in extract result will lead to deduction of 3 points
    if len(extract_prob) > len(correct_prob):
        diff = len(extract_prob) - len(correct_prob)
        curr_score -= 3 * diff


    #print('correct_prob is: ' + str(correct_prob))
    #print('extract_prob is: ' + str(extract_prob))
    
    each_score = symp_score / len(correct_prob)
    for each in correct_prob:
        if each in extract_prob:
            curr_score += each_score

    # Then check form
    correct_form_list = []
    extract_form_list = []
    correct_form = []
    extract_form = []
    for i in range(1, len(correct)):
        correct_form_list.append(correct[i][5])
    correct_form = get_all_content(correct_form_list)

    for i in range(len(extract)):
        extract_form_list.append(extract[i][5])
    extract_form = get_all_content(extract_form_list)

    for i in range(len(extract_form)):
        extract_form[i] = extract_form[i].split('_')[-1]

    #print('correct_form is: ' + str(correct_form))
    #print('extract_form is: ' + str(extract_form))

    # Check if extract_form has useful information
    for ele in extract_form:
        if ele in correct_prob:
            curr_score += 0.6 * each_score
    
    if len(correct_form) == 0 and len(extract_form) == 0:
        curr_score += form_score
        return curr_score

    if len(extract_form) > len(correct_form):
        diff = len(extract_form) - len(correct_form)
        curr_score -= diff
    if len(correct_form) == 0:
        correct_form.append('')

    # Total score for form is 5
    each_score = form_score / len(correct_form)
    for each in correct_form:
        if each in extract_form:
            curr_score += each_score

    return curr_score

def calculate_others(correct, extract):
    curr_score = 0

    correct_severity = correct[1][6]
    extract_severity = extract[0][6]

    if correct_severity == extract_severity:
        curr_score += 5

    correct_suddenness = correct[1][8]
    extract_suddenness = extract[0][8]

    if correct_suddenness == extract_suddenness:
        curr_score += 5

    correct_frequency = correct[1][9]
    extract_frequency = extract[0][9]

    if correct_frequency == extract_frequency:
        curr_score += 5

    correct_time = correct[1][10]
    extract_time = extract[0][10]

    if correct_time == extract_time:
        curr_score += 5

    return curr_score

def calculate_location(correct, extract):
    curr_score = 0.0
    total_score = 5.0

    correct_location = get_all_content(correct[1][1])
    extract_location = get_all_content(extract[0][1])

    for i in range(len(extract_location)):
        extract_location[i] = extract_location[i].split('_')[-1]

    #print('correct_location is ' + str(correct_location))
    #print('extract_location is ' + str(extract_location))
    if len(extract_location) > len(correct_location):
        diff = len(extract_location) - len(correct_location)
        curr_score -= diff

    if len(correct_location) == 0 and len(extract_location) == 0:
        curr_score = total_score
        return curr_score
    elif len(correct_location) == 0 and len(extract_location) != 0:
        return curr_score

    each_score = total_score / len(correct_location)

    for each in correct_location:
        if each in extract_location:
            curr_score += each_score

    return curr_score

def calculate_disease_part(correct, extract, index, total_score):
    curr_score = 0

    correct_disease = correct[1][index]
    extract_disease = extract[0][index]

    for i in range(len(extract_disease)):
        extract_disease[i] = extract_disease[i].split('_')[-1]

    #print('correct list is ' + str(correct_disease))
    #print('extract list is ' + str(extract_disease))

    if len(correct_disease) == 0 and len(extract_disease) == 0:
        curr_score = total_score
        return curr_score
    elif len(correct_disease) == 0 and len(extract_disease) != 0:
        return curr_score

    each_score = total_score / len(correct_disease)

    for each in correct_disease:
        if each in extract_disease:
            curr_score += each_score

    return curr_score


# Main function starts here
i = 0
lines = read_file()
extractor = Extractor()
overall = 0
scores = []
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
    print('Organ score: %.1f/30' % organ_score)

    location_score = calculate_location(one_set, result)
    print('Location score: %.1f/5' % location_score)

    symp_score = calculate_symp_part(one_set, result)
    print('Symp score: %.1f/35' % symp_score)

    others_score = calculate_others(one_set, result)
    print('Other score: %.1f/20' % others_score)

    not_included_score = calculate_disease_part(one_set, result, 7, 4.0)
    print('Not included score: %.1f/4' % not_included_score)

    history_score = calculate_disease_part(one_set, result, 14, 2.0)
    print('History score: %.1f/2' % history_score)
    suspect_score = calculate_disease_part(one_set, result, 15, 2.0)
    print('Suspect score: %.1f/2' % suspect_score)
    eliminate_score = calculate_disease_part(one_set, result, 16, 2.0)
    print('Eliminate score: %.1f/2' % eliminate_score)

    total = 0
    total += organ_score + location_score + symp_score + others_score
    total += not_included_score + history_score + suspect_score + eliminate_score 

    print('Total: %.1f/100' % total)

    overall += total
    scores.append(total)

    i += 18
    print('\n')
    print('----------------------------------------------------------')
    extractor.reset()

average = overall/100.0
print('Average is %.2f' % average)
median = statistics.median(scores)
print('Median is %.2f' % median)

above90 = 0
bw8090 = 0
bw7080 = 0
bw6070 = 0
bw5060 = 0
bw4050 = 0
bw3040 = 0
bw2030 = 0
bw1020 = 0
below10 = 0

for each in scores:
    if each >= 90:
        above90 += 1
    elif each >= 80:
        bw8090 += 1
    elif each >= 70:
        bw7080 += 1
    elif each >= 60:
        bw6070 += 1
    elif each >= 50:
        bw5060 += 1
    elif each >= 40:
        bw4050 += 1
    elif each >= 30:
        bw3040 += 1
    elif each >= 20:
        bw2030 += 1
    elif each >= 10:
        bw1020 += 1
    else:
        below10 += 1

print('>90: %d; 80~90: %d; 70~80: %d; 60~70: %d; 50~60: %d; 40~50: %d; 30~40: %d; 20~30: %d; 10~20: %d; <10: %d' % (above90, bw8090, bw7080, bw6070, bw5060, bw4050, bw3040, bw2030, bw1020, below10))
