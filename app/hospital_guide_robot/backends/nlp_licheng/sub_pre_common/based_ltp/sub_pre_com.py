# -*- coding: utf-8 -*-

import codecs
import os
import sys
from ltp_parse import LTP_parse
import time
import threading 

#initial LTP_parse()
ltp_parser = LTP_parse()
names = locals()

class Sub_Pre:
    def __init__(self, file_dir, sub_list, pre_list):
        #load dict 
        self.sub_list = sub_list
        self.pre_list = pre_list
        self.sub_word_id_dict = self.mu_create_word_id_dict(file_dir, sub_list)
        self.sub_id_word_dict = self.mu_create_id_word_dict(file_dir, sub_list)
        self.pre_word_id_dict = self.mu_create_word_id_dict(file_dir, pre_list)
        self.pre_id_word_dict = self.mu_create_id_word_dict(file_dir, pre_list)

        for sub in sub_list:
            sub_path = os.path.join(file_dir, sub)
            sub_name = sub
            names['self.%s_word_id_dict' %sub] = self.create_word_id_dict(sub_path)
            names['self.%s_raw_word_id_dict' %sub] = self.create_raw_word_id_dict(sub_path)
            names['self.%s_id_word_dict' %sub] = self.create_id_word_dict(sub_path)
        for pre in pre_list:
            pre_path = os.path.join(file_dir, pre)
            pre_name = pre
            names['self.%s_word_id_dict' %pre] = self.create_word_id_dict(pre_path)
            names['self.%s_id_word_dict' %pre] = self.create_id_word_dict(pre_path)

        #res_file save result data
        self.res_file_name = sub.split('_')[0] + '_'  + pre.split('_')[0]

        #sub_pre dict
        self.sub_pre_dict = {}
        self.tid = 0

    def add_dict(self,sub_word,pre_word):                
        if sub_word in self.sub_pre_dict and pre_word in self.sub_pre_dict[sub_word]:
            self.sub_pre_dict[sub_word][pre_word] += 1 
        if sub_word in self.sub_pre_dict and pre_word not in self.sub_pre_dict[sub_word]:                                                    
            self.sub_pre_dict[sub_word].update({pre_word:1})
        if sub_word not in self.sub_pre_dict:                           
            self.sub_pre_dict.update({sub_word:{pre_word:1}})
    
    def parse_dict(self):
        for sub in self.sub_list:
            for pre in self.pre_list:
                names['%s_%s_dict' %(sub,pre)] = {}

        for key1,key2_value in self.sub_pre_dict.items():
            #sorted larger to small
            #key1 is string ,key2_value is dict
            #parse to sub and pre
            #
            temp_key1 = ''
            temp_sub = ''
            for sub in self.sub_list:
                if key1 in names['self.%s_raw_word_id_dict' %sub].keys():
                    temp_sub = sub
                    temp_key1 = key1
            for pre in self.pre_list:
                for key2 ,val in key2_value.items():
                    if key2 in names['self.%s_word_id_dict' %pre].keys():
                        #print('sub:%s pre:%s val:%d' %(temp_key1,key2,val))
                        if temp_key1 in names['%s_%s_dict' %(temp_sub,pre)].keys():
                            names['%s_%s_dict' %(temp_sub,pre)][temp_key1].update({key2:val})
                        else:
                            names['%s_%s_dict' %(temp_sub,pre)].update({temp_key1:{key2:val}})
                        
        for sub in self.sub_list:
            for pre in self.pre_list:
                print('SUB_PRE:%s\t%s' %(sub,pre))
                sub_name = sub.split('_')[0]
                pre_name = pre.split('_')[0]
                f_name = sub_name + '_'+ pre_name
                save_f = open('res_sub_pre/%s' %f_name,'w')

                for key1,key2_value in names['%s_%s_dict' %(sub,pre)].items():
                    #print('key1:%s key2_val:%s' %(key1,key2_value))
                    sorted_pre = sorted(key2_value.items(),key = lambda 
                                        item:item[1],reverse = True)
                    num = 0                     
                    print("%s\t" %key1,end = '')
                    save_f.write("%s\t" %key1)   
                    sys.stdout.flush()
                    for line in sorted_pre:
                        if num < 10:
                            print('%s:%d' %(line[0],line[1]),end = '\t')
                            save_f.write('%s:%d\t'%(line[0], line[1]) )
                            sys.stdout.flush()
                            num += 1
                    print('\n',end = '')
                    save_f.write('\n')
                print("~EOF:")
                save_f.close()

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
        words, arcs = ltp_parser.des_parse(des)
        temp_sub = {} #key is word ,val is index
        temp_pre = {} #key is index ,val is word
        for i in range(len(words)):
            if words[i] in self.sub_word_id_dict.keys():
                id_val = self.sub_word_id_dict[words[i]]
                temp_sub[self.sub_id_word_dict[id_val]] = i + 1
            if words[i] in self.pre_word_id_dict.keys():
                temp_pre[i + 1] = words[i]    #self.pre_id_word_dict[id_val]
        if temp_sub and temp_pre:
            time4 = time.time()
            #print('---------------------------------------------')
            #print(des)
            #print('\t'.join(str(i + 1) for i in range(0, len(list(words)))))
            #print('\t'.join(word for word in list(words)))
            #print('\t'.join("%d:%s" % (arc.head, arc.relation) for arc in arcs))
            #print("find sub pre are: %s: %s" %(temp_sub, temp_pre))
            self.identify_sub_pre(temp_sub, temp_pre, arcs)

    def file_find_sub_pre(self, des_dir):
        file_num = len(os.listdir(des_dir))
        count = 0
        for line in os.listdir(des_dir):
            print('thread %d start file %d  all file num:%d' %(self.tid,count,file_num))
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

    def create_raw_word_id_dict(self, inFile):
        res_dict = {} #key is word,val is id
        temp_file = codecs.open(inFile, 'r', 'utf-8').readlines()
        for i in range(len(temp_file)):
            words = temp_file[i].strip()
            res_dict[words] = i
        return res_dict

    def mu_create_word_id_dict(self,file_dir,file_list):
        res_dict = {}
        dict_val = 0
        for file_name in file_list:
            file_path = os.path.join(file_dir,file_name)
            temp_file = codecs.open(file_path, 'r', 'utf-8').readlines()
            for line in temp_file:
                words = line.split()
                for ele in words:
                    res_dict[ele] = dict_val
                dict_val += 1
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

    def mu_create_id_word_dict(self, file_dir, file_list):
        res_dict = {} #key is id, val is the word,val is a list
        dict_key = 0
        for file_name in file_list:
            file_path = os.path.join(file_dir, file_name)
            temp_file = codecs.open(file_path, 'r', 'utf-8').readlines()
            for ele in temp_file:
                temp = ele.strip() #
                res_dict[dict_key] = temp
                dict_key += 1
        return res_dict

    def delete_match(self):
        del self.sub_pre_dict

    def work_thread(self,tid,des_dir):
        self.tid = tid
        self.file_find_sub_pre(des_dir)
    

if __name__ == '__main__':
    dict_file_dir = '/data/user/licheng/project/app/hospital_guide_robot/backends/nlp_licheng/dict.new'
    #ori_file_dir = '/data/user/licheng/project/app/hospital_guide_robot/backends/nlp_licheng/ori'
    ori_file_dir = '/data/nlp/corpus.predict_disease/1.ori'
    
    sub_list = ['organ_nlp','tissue_nlp','indicator_nlp','function_nlp','nutrition_nlp']
    pre_list = ['problem_nlp','appearance_nlp']
    
    sp = Sub_Pre(dict_file_dir, sub_list, pre_list)
    sp.file_find_sub_pre(ori_file_dir)    
