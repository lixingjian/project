# -*- coding: utf-8 -*-

import codecs
import sys
from pinyin import PinYin

class NameSearch:
    def __init__(self):
        self.name_yin_dict = self.get_name_yin_dict('name_pinyin_dict')
        self.score_thre = 50

    def calculate_score(self,name, name_yin):
        name_dict = {}
        for key, val in self.name_yin_dict.items():
            scores = self.fun1(name, key) + self.fun2(name_yin, val)
            #add dict
            if scores >= self.score_thre:
                name_dict[key] = scores
        return name_dict

    def run(self,name):
        name_yin = self.hanzi2yin(name)
        name_dict = self.calculate_score(name,name_yin)
        name_dict_sort = sorted(name_dict.items(), key = lambda
                                item:item[1], reverse = True)
        print(name_dict_sort)

    def get_name_yin_dict(self,path):
        name_yin_dict = {}
        name_yin_file = open(path,'r')
        for name_yin in name_yin_file:
            name_yin_list = name_yin.split('\t')
            name = name_yin_list[0]
            yin = name_yin_list[1].strip('\n')
            name_yin_dict[name] = yin
        return name_yin_dict
    '''
        Define evaluation function
        function1:same form 0-100
                2:same yin but different form
                3:different yin
                4:different tone
    '''
    #fun1 use the same number of word1/word2 to 
    #culculate the similarity of two words
    def fun1(self, word1, word2):
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
        score = num / len( word1 ) * 100.0
        return score

    def fun2(self,word1_yin, word2_yin):
        score = 0
        if word1_yin == word2_yin:
            score = 100
        return score

    def hanzi2yin(self, hanzi):
        py = PinYin()
        py.load_word()
        yin_list = py.hanzi2pinyin(string = hanzi)
        return ' '.join(yin_list)

if __name__ == "__main__":
    ns = NameSearch()
    name = input("please input:")
    ns.run(name)    
         
