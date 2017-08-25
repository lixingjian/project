# -*- coding: utf-8 -*-

import codecs
import os
LTP_DATA_DIR = '/Users/Herman/Documents/BOE/pyltp/ltp_data'
cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')
pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')
par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')
LEXICON_PATH = '/Users/Herman/Documents/BOE/project.git/app/hospital_guide_robot/backends/nlp_haozhe/all_nlp'

from pyltp import Segmentor
from pyltp import Postagger
from pyltp import Parser
#from Match import Match

class Extractor:
    def __init__(self):
        self.segmentor = Segmentor()
        self.segmentor.load_with_lexicon(cws_model_path, LEXICON_PATH)
        self.postagger = Postagger()
        self.postagger.load(pos_model_path)
        self.parser = Parser()
        self.parser.load(par_model_path)

        # Load all lists with the input files
        self.organ_list = self.load_list('organ_nlp')
        self.location_list = self.load_list('location_nlp')
        self.tissue_list = self.load_list('tissue_nlp')
        self.indicator_list = self.load_list('indicator_nlp')
        self.problem_list = self.load_list('problem_nlp')
        self.feeling_list = self.load_list('feeling_nlp')
        self.severity_dict = self.load_dict('severity_nlp')
        # self.symp_list = self.load_list('symp_nlp')
        self.suddenness_dict = self.load_dict('suddenness_nlp')
        self.frequency_dict = self.load_dict('frequency_nlp')
        self.time_dict = self.load_dict('time_nlp')
        self.disease_list = self.load_list('disease_nlp')
        self.negative_list = self.load_list('negative_nlp')
        self.prob_temp = []
        self.form_temp = []
        self.in_prob_list = []

    def reset(self):
        self.prob_temp = []
        self.form_temp = []
        self.in_prob_list = []


    def extract(self, description):
        #matcher = Match()
        #synDict = matcher.createSynDict('syn1.txt', 'symp_nlp')
        #description = matcher.replaceSyn(description, synDict)
        print(description)
        words = self.segmentor.segment(description)
        postags = self.postagger.postag(words)
        arcs = self.parser.parse(words, postags)

        print ('\t'.join(str(i + 1) for i in range(0, len(list(words)))))
        print('\t'.join(word for word in list(words)))
        print ("\t".join("%d:%s" % (arc.head, arc.relation) for arc in arcs))

        num_of_tuple = self.find_num_of_tuple(words, arcs)
        tuples = []

        for num in range(num_of_tuple):
            tuples.append(self.construct_tuple(description, num))

        return tuples

    def construct_tuple(self, description, num):
        """
        Tuple格式如下：

        ( [器官A，器官B ... ],    [ [器官A方位],[器官B方位] ...],
        [人体组织],
         [人体指标],     [问题或感觉],     [问题或感觉的形式],
          int(问题或感觉的程度),     [不包含症状],     int(症状出现缓急),
           int(症状出现频率),     int(症状出现时间),     int(症状持续时间),
            str(起因，暂不填写),     str(加剧因素，暂不填写),
            str(缓解因素，暂不填写),
             [病史],     [怀疑疾病],     [排除疾病] )
        """

        res = ()
        words = self.segmentor.segment(description)
        postags = self.postagger.postag(words)
        arcs = self.parser.parse(words, postags)

        # Initialize all elements in the tuple
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

        # Iterate through every single word
        for i in range(len(words)):
            # Get organs and their locations
            if words[i] in self.organ_list:
                if not ('O_' + words[i]) in organs:
                    organs.append('O_' + words[i])
                    temp_location = self.find_location(words, arcs, i)
                    location.append(temp_location)
            # Get tissue
            elif words[i] in self.tissue_list and not ('T_' + words[i]) in tissue:
                tissue.append('T_' + words[i])
            # Get indicator
            elif words[i] in self.indicator_list and not ('I_' + words[i]) in indicator:
                indicator.append('I_' + words[i])
            #elif words[i] in self.problem_list and not ('P_' + words[i]) in problem:
                #problem.append('P_' + words[i])
            # Get severity
            elif words[i] in self.severity_dict:
                severity = max(int(self.severity_dict.get(words[i])), severity)
            # Get suddenness
            elif words[i] in self.suddenness_dict:
                suddenness = int(self.suddenness_dict.get(words[i]))
            # Get frequency
            elif words[i] in self.frequency_dict:
                frequency = int(self.frequency_dict.get(words[i]))
            # Get problems that are not part of the actual symptom
            # 处理有否定含义的信息
            elif words[i] in self.negative_list:
                self.find_not_included(list(words), i, words[i], arcs, not_included)
            elif words[i] in self.disease_list:
                pass
            elif words[i] in self.time_dict:
                time = max(int(self.time_dict.get(words[i])), time)

        for each in description:
            if each in self.severity_dict:
                severity = int(self.severity_dict.get(each))
                
        # Get the problems
        temp_problem = self.find_problem(words, arcs, num)
        for ele in temp_problem:
            if  ele in problem or ('P_' + ele) in problem:
                continue
            if ele in self.problem_list:
                problem.append('P_' + ele)
            else:
                problem.append(ele)

        head_index = self.find_head_index(arcs)
        # Remove the duplicates
        for ele in not_included:
            if ele in problem: #and words[head_index] != ele:
                problem.remove(ele)
            if ele in organs:
                index = organs.index(ele)
                location.remove(location[index])
                organs.remove(ele)
            if ele in tissue:
                tissue.remove(ele)
            if ele in indicator:
                indicator.remove(ele)

        temp_form = self.find_form(words, arcs, num)
        for ele in temp_form:
            form.append(ele)
        for ele in temp_form:
            for each in location:
                if ele in each or ('L_' + ele) in each:
                    form.remove(ele)
        
        history = self.find_disease(description, 'history_nlp')
        suspect = self.find_disease(description, 'suspect_nlp')
        eliminate = self.find_disease(description, 'eliminate_nlp')

        """
        to_remove = ''
        for ele in history:
            for another in eliminate:
                if ele == another:
                    to_remove = ele
        if to_remove != '':
            suspect.append(to_remove)
            history.remove(to_remove)
            eliminate.remove(to_remove)
        """

        # Formatting the output of tuple
        res = self.format_tuple(res, organs, 'Organ')
        res = self.format_tuple(res, location, 'Location')
        res = self.format_tuple(res, tissue, 'Tissue')
        res = self.format_tuple(res, indicator, 'Indicator')
        res = self.format_tuple(res, problem, 'Problem')
        res = self.format_tuple(res, form, 'Form')
        res +=  (severity,) 
        res = self.format_tuple(res, not_included, 'Not_included')
        res +=  (suddenness,) + (frequency,) + (time,)
        res +=  (trigger,) + (worsen,) + (relief,)
        res = self.format_tuple(res, history, 'History')
        res = self.format_tuple(res, suspect, 'Suspect')
        res = self.format_tuple(res, eliminate, 'Eliminate')
        return res

    def format_tuple(self, res, in_list, name):
        #if len(in_list) == 0:
        #    res += ([ name + ' list is empty'],)
        #else:
        #    res += (in_list,)
        res += (in_list,)
        return res

    # Helper method to find the word index of head
    def find_head_index(self, arcs):
        k = 0
        head_index = 0
        for arc in arcs:
            if arc.head == 0:
                head_index = k
                break
            k += 1
        return head_index

    # Helper method to find all children of the current word
    # i is the index of curr_word in [words]
    def find_children(self, words, i, curr_word, arcs):
        children = []
        k = 0
        for arc in arcs:
            if arc.head == i + 1 and arc.relation != 'COO' and arc.relation != 'WP':
                children.append((words[k], k))
            k += 1
        return children

    def find_form(self, words, arcs, num):
        form = []
        head_index = self.find_head_index(arcs)
        if num == 0:
            children = self.find_children(words, head_index, words[head_index], arcs)
            for child, index in children:
                if arcs[index].relation == 'ADV' or arcs[index].relation == 'VOB':
                    if not child in self.form_temp and not child in self.location_list:
                        form.append(child)
                        self.form_temp.append(child)

        else:
            j = 0
            k = 0
            for arc in arcs:
                if arc.head == head_index + 1 and arc.relation == 'COO':
                    j += 1
                    if j == num:
                        children = self.find_children(words, k, words[k], arcs)
                        for child, index in children:
                            if arcs[index].relation == 'ADV' or arcs[index].relation == 'VOB':
                                if not child in self.form_temp and not child in self.location_list:
                                    form.append(child)
                                    self.form_temp.append(child)
                k += 1

        return form


    # 处理否定含义的信息 
    # Recursive method that gets all children of the negative word e.g.
    # ‘不’，‘没有’，‘无’ 等
    def find_not_included(self, words, i, curr_word, arcs, not_included):
        children = self.find_children(words, i, curr_word, arcs)
        copy = []
        for ele in children:
            copy.append(ele)
        for ele, index in copy:
            if arcs[index].relation == 'ADV':
                children.remove((ele, index))
        
        # Base case
        if arcs[i].relation != 'ADV':
            if len(children) == 0:
                return

        temp1 = []
        temp2 = []
        index_list = []

        # If curr_word has a relation of ADV to its parent node, add its parent
        # to not_included. Then add all children (including grandchildren and
        # more) of its parent to not_included.
        if arcs[i].relation == 'ADV' and not words[arcs[i].head - 1] in temp1:
            if arcs[arcs[i].head - 1].head != 0:
                curr = words[arcs[i].head - 1]
                temp1.append(curr)
                if curr in self.organ_list:
                    not_included.append('O_' + curr)
                elif curr in self.location_list:
                    not_included.append('L_' + curr)
                elif curr in self.tissue_list:
                    not_included.append('T_' + curr)
                elif curr in self.indicator_list:
                    not_included.append('I_' + curr)
                elif curr in self.feeling_list:
                    not_included.append('F_' + curr)
                elif curr in self.problem_list:
                    not_included.append('P_' + curr)
                else:
                    not_included.append(curr)
                i += 1
        
        # If curr_word is not an adverb, add all its childre (including
        # grandchildren and more) to not_included
        for child, index in children:
            #if arcs[index].relation == 'ADV':
                #continue
            if not child in temp2 and child != '不':
                if child in self.organ_list:
                    not_included.append('O_' + child)
                elif child in self.location_list:
                    not_included.append('L_' + child)
                elif child in self.tissue_list:
                    not_included.append('T_' + child)
                elif child in self.indicator_list:
                    not_included.append('I_' + child)
                elif child in self.feeling_list:
                    not_included.append('F_' + child)
                elif child in self.problem_list:
                    not_included.append('P_' + child)
                else:
                    not_included.append(child)
                temp2.append(child)
        
        # Recursive call    
        k = 0
        for each in temp2:
            self.find_not_included(words, children[k][1], each, arcs, not_included)
            k += 1

    # Find location words
    def find_location(self, words, arcs, organ_index):
        location = []
        k = 0
        for arc in arcs:
            if k == organ_index:
                head_val = arc.head
                if words[head_val - 1] in self.location_list:
                    location.append('L_' + words[head_val - 1])
                elif arc.relation == 'ATT':
                    location.append(words[head_val - 1])
                    j = 0
                    for arc2 in arcs:
                        if arc2.head == head_val and arc2.relation == 'COO':
                            if words[j] in self.location_list:
                                location.append('L_' + words[j])
                            else:
                                location.append(words[j])
                        j += 1
            k += 1
        return location

    # Find the words that describe problem
    def find_problem(self, words, arcs, num):
        problem = []
        head_index = self.find_head_index(arcs)
        if num == 0:
            # Add head to the list
            if words[head_index] in self.feeling_list and not words[head_index] in self.prob_temp:
                problem.append('F_' + words[head_index])
                self.prob_temp.append(words[head_index])
            elif words[head_index] in self.problem_list and not words[head_index] in self.prob_temp:
                problem.append('P_' + words[head_index])
                self.prob_temp.append(words[head_index])
            elif not words[head_index] in self.prob_temp:
                problem.append(words[head_index])
                self.prob_temp.append(words[head_index])

        else:
            # Add the corresponding COO words of head to the list
            j = 0
            k = 0
            found_COO = False
            for arc in arcs:
                if arc.head == head_index + 1 and arc.relation == 'COO':
                    j += 1
                    if j == num:
                        if words[k] in self.feeling_list and not words[k] in self.prob_temp:
                            problem.append('F_' + words[k])
                            self.prob_temp.append(words[k])
                            found_COO = True
                            break
                        elif words[k] in self.problem_list and not words[k] in self.prob_temp:
                            problem.append('P_' + words[k])
                            self.prob_temp.append(words[k])
                            found_COO = True
                            break
                        elif not words[k] in self.prob_temp:
                            problem.append(words[k])
                            self.prob_temp.append(words[k])
                            found_COO = True
                            break
                        else:
                            return problem
                k += 1
            
            if not found_COO:
                for word in words:
                    if word in self.problem_list and not word in self.in_prob_list and not word in self.prob_temp:
                        self.in_prob_list.append(word)

                index = num - j - 1
                problem.append('P_' + self.in_prob_list[index])

        return problem

    def find_disease(self, description, input_file):
        for punc in [u'。',' ',u'！',u'？',u'；',u'：',',','.','?','!']:
            description.replace(punc, '，')
        desc_list = description.split('，')
        keyword_list = self.load_list(input_file)
        result = []
        for each in desc_list:
            for ele in keyword_list:
                if each.find(ele.rstrip()) >= 0:
                    words = self.segmentor.segment(each)
                    for word in words:
                        if word in self.disease_list and not ('D_' + word) in result:
                            result.append('D_' + word)
        return result

    # Find subject words
    def find_subject(self, words, arcs):
        subject = []
        head_index = self.find_head_index(arcs)
        j = 0
        for arc in arcs:
            if arc.head == head_index + 1 and arc.relation == 'SBV':
                subject.append(words[j])
            j += 1
        return subject

    def find_num_of_tuple(self, words, arcs):
        head_index = self.find_head_index(arcs)
        temp = []
        temp.append(words[head_index])
        j = 1
        k = 0
        for arc in arcs:
            if arc.head == head_index + 1 and arc.relation == 'COO':
                if not words[k] in self.problem_list and not words[k] in temp: 
                    temp.append(words[k])
                    j += 1
            k += 1

        for word in words:
            if word in self.problem_list and not word in temp:
                temp.append(word)
                j += 1

        return j

    # Helper method to load a list from a file
    def load_list(self, inFile):
        res_list = []
        temp_list = codecs.open(inFile, 'r', 'utf-8').readlines()
        for ele in temp_list:
            temp = ele.split()[0].rstrip()
            res_list.append(temp)
        return res_list

    # Helper method to laod a dictionary from a file
    def load_dict(self, inFile):
        res_dict = {}
        temp_list = codecs.open(inFile, 'r', 'utf-8').readlines()
        for ele in temp_list:
            key = ele.split()[0].rstrip()
            val = ele.split()[-1].rstrip()
            res_dict[key] = val
        return res_dict

    # Method to release the modles. Call this at the end of the program
    def release(self):
        self.segmentor.release()
        self.postagger.release()
        self.parser.release()

if __name__ == '__main__':
    extractor = Extractor()
    i = 0
    ans = input('Long test or short test? (L or l for long, S or s for short)')
    if ans == 'S' or ans == 's':
        while i < 3:
            userInput = input(u'请输入: ')
            if len(userInput) == 0:
                i += 1
                continue
            res = extractor.extract(userInput)
            for ele in res:
                print(ele)
                print()
            i += 1
            extractor.reset()
        extractor.release()
    else:
        f = codecs.open('symptom_input.txt', 'r', 'utf-8')
        for line in f.readlines():
            res = extractor.extract(line)
            for ele in res:
                print(ele)
                print()
            extractor.reset()
        extractor.release()
