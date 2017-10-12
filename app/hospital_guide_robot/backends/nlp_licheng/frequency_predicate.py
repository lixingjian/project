# -*- coding: utf-8 -*-

"""
author by Chenlee
created:2017-9-27

"""
import os
import sys
import codecs

class Frequency:
    def __init__(self,sub_path, pre_path):
        self.file_name = sub_path + pre_path
        self.sub_lines = codecs.open(sub_path,'r','utf-8')
        self.pre_lines = codecs.open(pre_path,'r','utf-8')
        #for line in sub_lines:
            #print(line.strip('\n'))
        
    def freq(self, description_path):
        print('--------------------------------------')
        print(self.file_name)
        for sub_line in self.sub_lines: 
            #print(sub_line)
            fre = {} #key 为副词，value为次数  
            for file_name in os.listdir(description_path):
                des_path = os.path.join(description_path, file_name)
                #Get description
                des_lines = codecs.open(des_path, 'r','utf-8') 
                for des_line in des_lines:
                    #every description
                    #print(des_line)
                    if sub_line.strip('\n') in des_line:
                        for pre_line in self.pre_lines:
                            if pre_line.strip('\n') in des_line:
                                try:
                                    fre[pre_line.strip('\n')] += 1
                                except:
                                    fre[pre_line.strip('\n')] = 1
                    else:
                        continue
            fre = sorted(fre.items(), key = lambda asd:asd[0] , reverse = False)
            print('%s:'%sub_line.strip('\n'),end = '')
            sys.stdout.flush()
            if len(fre) >= 0 :
                num = 0
                for fre_key in fre:
                    if num < 10:
                        print(fre_key,end = '')
                        sys.stdout.flush()
                        num += 1
            print('\n',end = '')
        print('**************************************')   
        
        
if __name__ == '__main__':
    frequency = Frequency('organ_nlp', 'problem_nlp')
    frequency.freq('/data/nlp/corpus.predict_disease/1.ori')


    frequency1 = Frequency('organ_nlp', 'appearance_nlp')
    frequency1.freq('/data/nlp/corpus.predict_disease/1.ori')
 


    frequency = Frequency('tissue_nlp', 'problem_nlp')
    frequency.freq('/data/nlp/corpus.predict_disease/1.ori')


    frequency1 = Frequency('tissue_nlp', 'appearance_nlp')
    frequency1.freq('/data/nlp/corpus.predict_disease/1.ori')


    frequency = Frequency('indicator_nlp', 'problem_nlp')
    frequency.freq('/data/nlp/corpus.predict_disease/1.ori')


    frequency1 = Frequency('indicator_nlp', 'appearance_nlp')
    frequency1.freq('/data/nlp/corpus.predict_disease/1.ori')


    frequency = Frequency('function_nlp', 'problem_nlp')
    frequency.freq('/data/nlp/corpus.predict_disease/1.ori')


    frequency1 = Frequency('function_nlp', 'appearance_nlp')
    frequency1.freq('/data/nlp/corpus.predict_disease/1.ori')


    frequency = Frequency('nutrition_nlp', 'problem_nlp')
    frequency.freq('/data/nlp/corpus.predict_disease/1.ori')


    frequency1 = Frequency('nutrition_nlp', 'appearance_nlp')
    frequency1.freq('/data/nlp/corpus.predict_disease/1.ori')
