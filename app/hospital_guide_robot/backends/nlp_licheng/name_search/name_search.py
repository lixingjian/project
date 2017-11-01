# -*- coding: utf-8 -*-

import codecs
import sys
from pinyin import PinYin

class NameSearch:
    def __init__(self):
        self.name_yin_tone_dict = self.get_name_yin_tone_dict('name_yin_tone_dict')
        self.score_thre = 0.67
    
    def calculate_score(self,name, yin, tone):
        name_dict = {}
        for key, val in self.name_yin_tone_dict.items():
            lib_name = key
            lib_yin = val.split(':')[0]
            lib_tone = val.split(':')[1].strip('\n')
            w = 0.01 / 3
            scores = w * self.fun1(name, lib_name) + w * self.fun2(yin, lib_yin) + w * self.fun3(tone, lib_tone)
            #add dict
            if scores >= self.score_thre:
                name_dict[key] = scores
        return name_dict

    def run(self,name):
        yin, tone = self.hanzi2yintone(name)
        name_dict = self.calculate_score(name, yin, tone)
        name_dict_sort = sorted(name_dict.items(), key = lambda
                                item:item[1], reverse = True)
        print(name_dict_sort)
        name_list = []
        for ele in name_dict_sort:
            name_list.append(ele[0])
        return name_list

    def get_name_yin_tone_dict(self,path):
        name_yin_tone_dict = {}
        name_yin_tone_file = open(path,'r')
        for name_yin_tone in name_yin_tone_file:
            name_yin_tone_list = name_yin_tone.split('\t')
            name = name_yin_tone_list[0]
            yin_tone = name_yin_tone_list[1].strip('\n')
            name_yin_tone_dict[name] = yin_tone
        return name_yin_tone_dict

    '''
        Define evaluation function
        function1:same form 0-100
                2:same yin 0-100
    '''
    #fun1 use the same number of word1/word2 to 
    #culculate the similarity of two words
    def fun1(self, word1, word2):
        if len(word2) != len(word1):
            return 0
        num = self.words_compare(word1, word2)
        score = num / len( word1 ) * 100.0
        return score

    def fun2(self,word1_yin, word2_yin):
        score = 0
        yin1_list = word1_yin.split(' ')
        yin2_list = word2_yin.split(' ')
        if len(yin1_list) != len(yin2_list):
            return 0    
        score_incre = 1 / len(yin1_list) * 100
        for i in range(len(yin1_list)):
            diff_char = self.string_compare(yin1_list[i], yin2_list[i])
            if diff_char == '':
                score += score_incre
                continue
            if len(diff_char) == 2:
                #if not distinguish 'l' 'n'
                #if not distinguish if there are 'g'
                if diff_char == 'ln' or diff_char == 'nl' or diff_char == ' g' or diff_char == 'g ':
                    score += score_incre - 20
            if len(diff_char) == 4:
                if diff_char == 'ln g' or diff_char == 'nl g' or diff_char == 'lng ' or diff_char == 'nlg ':
                    score -= score_incre - 25
            #initial_char_same
            if self.same_initial_char( yin1_list[i], yin2_list[i]):
                score += 5
        return score

    def fun3(self, word1_tone, word2_tone):
        if word1_tone == word2_tone:
            return 100
        return 0

    def same_initial_char(self,string1,string2):
        #print('%s %s:' %(string1,string2))
        if len(string1) == 0 or len(string2) == 0:
            return False
        if string1[0] == string2[0]:
            return True
        return False

    def string_align(self,string1,string2):
        l1 = len(string1)
        l2 = len(string2)
        if l1 > l2:
            for i in range(l1 - l2):
                string2 += ' '
        else:
            for i in range(l2 - l1):
                string1 += ' '
        return string1,string2

    #compare string1 and string2,return 
    def string_compare(self, string1, string2):
        if len(string1) != len(string2):
            string1, string2 = self.string_align(string1, string2)
        diff_char = ''
        for i in range(len(string1)):
            if  string1[i] != string2[i]:
                diff_char += string1[i] + string2[i]
        return diff_char

    #compare word1 and word2
    def words_compare(self, word1, word2):
        char_num = {}
        for ele in word1:
            if ele in char_num.keys():
                char_num[ele] += 1
            else:
                char_num[ele] = 1
        num = 0
        for ele in word2:
            if ele in char_num.keys():
                num += 1
        return num

    def hanzi2yintone(self, hanzi):
        py = PinYin()
        py.load_word()
        yin_list,tone_list = py.hanzi2yintone(string = hanzi)
        yin = ' '.join(yin_list)
        tone = ' '.join(tone_list)
        return yin,tone

if __name__ == "__main__":
    ns = NameSearch()
    # name = input("please input:")
    #ns.run(name)   

   
    name_file = open('name_dict','r')
    for name in name_file:
        print('name:%s' %name)
        ns.run(name.strip('\n'))
        print('--------------')
   
