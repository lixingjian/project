# -*- coding: utf-8 -*-

import codecs
import os
import sys
from ltp_parse import LTP_parse

class Sub_Pre:
    def __init__(self, file_dir, sub, pre):
        #load dict 
        sub_path = os.path.join(file_dir, sub)
        pre_path = os.path.join(file_dir, pre)
        self.sub_word_id_dict = self.create_word_id_dict(sub_path)
        self.sub_id_word_dict = self.create_id_word_dict(sub_path)
        self.pre_word_id_dict = self.create_word_id_dict(pre_path)
        self.pre_id_word_dict = self.create_id_word_dict(pre_path)
        #initial LTP_parse()
        self.ltp_parser = LTP_parse()

        #res_file save result data
        self.res_file_name = sub.split('_')[0] + '_'  + pre.split('_')[0]

        #two dimention dict
        '''
            for example:
                {organ_name:{problem_name1:frequency1,problem_name2:frequency2...}}
        '''
        self.sub_pre_dict = {}

    def add_dict(self,sub_word,pre_word):                
        if sub_word in self.sub_pre_dict and pre_word in self.sub_pre_dict[sub_word]:
            self.sub_pre_dict[sub_word][pre_word] += 1 
        if sub_word in self.sub_pre_dict and pre_word not in self.sub_pre_dict[sub_word]:                                                    
            self.sub_pre_dict[sub_word].update({pre_word:1})
        if sub_word not in self.sub_pre_dict:                           
            self.sub_pre_dict.update({sub_word:{pre_word:1}})

    def parse_dict(self):
        print('start_parse_dict!')
        res_file = open('res_sub_pre/%s' %self.res_file_name,'w')
        res_file.write(self.res_file_name+'\n')
        for key1,key2_value in self.sub_pre_dict.items():
            #sorted larger to small
            sorted_pre = sorted(key2_value.items(),key = lambda 
                                item:item[1],reverse = True)
            num = 0                     
            print("%s:" %key1,end = '')
            res_file.write("%s: " %key1)
            sys.stdout.flush()
            for line in sorted_pre:
                if num < 10:
                    print('%s%d' %(line[0],line[1]),end = '\t')
                    res_file.write('%s%d\t' %(line[0], line[1]))
                    sys.stdout.flush()
                    num += 1
            print('\n',end = '')
            res_file.write('\n')

    def identify_sub_pre(self, sub, pre, arcs):
        for sub_word in sub:
            sub_word_val = sub[sub_word]
            sub_pre_rela = arcs[sub_word_val - 1].relation
            if ("SBV" ==  sub_pre_rela or "ATT" == sub_pre_rela) and arcs[sub_word_val - 1].head in pre.keys():
                res_sub = sub_word
                res_pre = pre[ arcs[sub_word_val - 1].head ]
                print("real sub pre: %s %s" %(res_sub, res_pre))
                self.add_dict(res_sub, res_pre)

    def find_sub_pre_in_dict(self, des):
        words, arcs = self.ltp_parser.des_parse(des)
        temp_sub = {} #key is word ,val is index
        temp_pre = {} #key is index ,val is word
        for i in range(len(words)):
            if words[i] in self.sub_word_id_dict.keys():
                id_val = self.sub_word_id_dict[words[i]]
                temp_sub[self.sub_id_word_dict[id_val]] = i + 1
            if words[i] in self.pre_word_id_dict.keys():
                id_val = self.pre_word_id_dict[words[i]]
                temp_pre[i + 1] = words[i]    #self.pre_id_word_dict[id_val]
        if temp_sub and temp_pre:        
            print('---------------------------------------------')
            print(des)
            print('\t'.join(str(i + 1) for i in range(0, len(list(words)))))
            print('\t'.join(word for word in list(words)))
            print('\t'.join("%d:%s" % (arc.head, arc.relation) for arc in arcs))
            print("find sub pre are: %s %s" %(temp_sub, temp_pre))
            self.identify_sub_pre(temp_sub, temp_pre, arcs)

    def file_find_sub_pre(self, des_dir):
        for line in os.listdir(des_dir):
            #print(line)
            des_path = os.path.join(des_dir,line)
            all_des = codecs.open(des_path, 'r' ,'utf-8')
            for des in all_des:
                des_list = des.split('\t')
                self.find_sub_pre_in_dict(des_list[0])
        self.parse_dict()
            
    def create_word_id_dict(self, inFile):
        res_dict = {} #key is word,val is id
        temp_file = codecs.open(inFile, 'r', 'utf-8').readlines()
        for i in range(len(temp_file)):
            words = temp_file[i].split()
            for ele in words:
                res_dict[ele] = i
        return res_dict

    def create_id_word_dict(self, inFile):
        res_dict = {} #key is id, val is the word,val is a list
        temp_file = codecs.open(inFile, 'r', 'utf-8').readlines()
        i = 0
        for ele in temp_file:
            temp = ele.strip() #
            res_dict[i] = temp
            i += 1
        return res_dict

    def delete_match(self):
        del self.sub_pre_dict


if __name__ == '__main__':
    dict_file_dir = '/data/user/licheng/project/app/hospital_guide_robot/backends/nlp_licheng/dict'
    ori_file_dir = '/data/user/licheng/project/app/hospital_guide_robot/backends/nlp_licheng/ori'
    #ori_file_dir = '/data/nlp/corpus.predict_disease/1.ori'
    
    sub_list = ['organ_nlp','tissue_nlp','indicator_nlp','function_nlp','nutrition_nlp']
    pre_list = ['problem_nlp','appearance_nlp']
    for sub in sub_list:
        for pre in pre_list:
            sub_pre = Sub_Pre(dict_file_dir, sub, pre)
            sub_pre.file_find_sub_pre(ori_file_dir)
            sub_pre.delete_match()


