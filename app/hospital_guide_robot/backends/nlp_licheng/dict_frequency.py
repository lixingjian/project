# -*- coding: utf-8 -*-

'''
Author: chenlee
'''
import os
import sys
from Match import Match
import codecs

class Frequency:
    def __init__(self, file_dir, subject, predicate, dis):
        #add key to ahocorasick
        self.sub_match = Match()
        self.sub_match.load(os.path.join(file_dir,subject))

        self.pre_match = Match()
        self.pre_match.load(os.path.join(file_dir,predicate))

        #two dimention dict
        '''
            for example:
                {organ_name:{problem_name1:frequency1,problem_name2:frequency2...}}
        '''
        self.sub_dict = {}
        self.pre_dict = {}

        #distance between subject and predicate
        self.dis = dis
    #parse sub_dict  get the data like
    '''
        for example:
            手:发麻  冰凉  肿
            口角：发炎  肿痛
    '''
    def parse_dict(self):
        for key1,key2_value in self.sub_dict.items():
            #sorted larger to small
            sorted_pre = sorted(key2_value.items(),key = lambda item:item[1],reverse = True)
            sys.stdout.flush()
            num = 0
            print("%s:" %key1,end = '')
            for line in sorted_pre:
                if num < 10:
                    print(line[0],end = ' ')
                    sys.stdout.flush()
                    num += 1
            print('\n',end = '')

    def file_des_match(self, des_dir):
        #Read file and get dict
        for line in os.listdir(des_dir):
            des_path = os.path.join(des_dir,line)
            all_des = codecs.open(des_path, 'r' ,'utf-8')
            for des in all_des:
                self.des_match(des)
            self.parse_dict()     

    def add_dict(self,sub_word,pre_word):
        fre = 0
        if sub_word in self.sub_dict and pre_word in self.sub_dict[sub_word]:
            self.sub_dict[sub_word][pre_word] += 1 
        if sub_word in self.sub_dict and pre_word not in self.sub_dict[sub_word]:
            self.sub_dict[sub_word].update({pre_word:1})
        if sub_word not in self.sub_dict:
            self.sub_dict.update({sub_word:{pre_word:1}})

    def des_match(self, des):
        #subject match
        sub_match = self.sub_match.match(des)
        if sub_match:
            #predicate match
            pre_match = self.pre_match.match(des)
            if pre_match:
                sub_word = sub_match[0][1][1]
                pre_word = pre_match[0][1][1]
                dis = abs( sub_match[0][0] - pre_match[0][0])
                print('%s %s %d' %(sub_word, pre_word,dis))
                if dis < self.dis:
                    self.add_dict(sub_word,pre_word)      

if __name__ == '__main__':
    frequency = Frequency('dict/','organ_nlp','problem_nlp',10)
    #frequency.file_des_match('/data/nlp/corpus.predict_disease/1.ori/')#
    frequency.file_des_match('ori/')


                














