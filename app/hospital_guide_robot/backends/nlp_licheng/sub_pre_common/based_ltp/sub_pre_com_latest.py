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
        sub_name = 'sub'
        pre_name = 'pre'
        names['self.%s_list'%sub_name] = sub_list
        names['self.%s_list'%pre_name] = pre_list
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
            names['self.%s_raw_word_id_dict'%pre] = self.create_raw_word_id_dict(pre_path)
            names['self.%s_id_word_dict' %pre] = self.create_id_word_dict(pre_path)

        #res_file save result data
        self.res_file_name = sub.split('_')[0] + '_'  + pre.split('_')[0]

        #sub_pre dict
        sub_pre_name = 'sub_pre'
        pre_sub_name = 'pre_sub'
        names['self.%s_dict'%sub_pre_name] = {}
        names['self.%s_dict'%pre_sub_name] = {}
        self.pre_sub_dict = {}
        self.tid = 0
        self.pre_dict = {}   
        self.sub_dict = {}
    
    def add_dicts(self,key1,key2,dicts):                
        if key1 in dicts.keys() and key2 in dicts[key1].keys():
            dicts[key1][key2] += 1 
        if key1 in dicts.keys() and key2 not in dicts[key1].keys():              
            dicts[key1].update({key2:1})
        if key1 not in dicts.keys():                           
            dicts.update({key1:{key2:1}})
        return dicts
    
    def parse_dict(self, dicts, dict_name):
        dict_name_list = dict_name.split('_')
        for word1 in names['self.%s_list'%dict_name_list[0]]:
            for word2 in names['self.%s_list'%dict_name_list[1]]:
                names['%s_%s_dict' %(word1,word2)] = {}
        for key1,key2_value in names['self.%s_dict' %dict_name].items():
            #sorted larger to small
            #key1 is string ,key2_value is dict
            temp_key1 = ''
            temp_word1 = ''
            for word1 in names['self.%s_list' %dict_name_list[0]]:
                if key1 in names['self.%s_word_id_dict' %word1].keys():
                    temp_word1 = word1
                    temp_key1 = key1
            for word2 in names['self.%s_list' %dict_name_list[1]]:
                for key2 ,val in key2_value.items():
                    if key2 in names['self.%s_word_id_dict' %word2].keys():
                        #print('sub:%s pre:%s val:%d' %(temp_key1,key2,val))
                        if temp_key1 in names['%s_%s_dict' %(temp_word1,word2)].keys():
                            names['%s_%s_dict' %(temp_word1,word2)][temp_key1].update({key2:val})
                        else:
                            names['%s_%s_dict' %(temp_word1,word2)].update({temp_key1:{key2:val}})
                        
        for word1 in names['self.%s_list' %dict_name_list[0]]:
            for word2 in names['self.%s_list' %dict_name_list[1]]:
                print('word1_word2:%s\t%s' %(word1,word2))
                word1_name = word1.split('_')[0]
                word2_name = word2.split('_')[0]
                f_name = word1_name + '_'+ word2_name
                save_f = open('res_sub_pre/%s' %f_name,'w')
                for key1,key2_value in names['%s_%s_dict' %(word1,word2)].items():
                    #print('key1:%s key2_val:%s' %(key1,key2_value))
                    sorted_word2 = sorted(key2_value.items(),key = lambda 
                                        item:item[1],reverse = True)
                    num = 0    
                    dict_num = 0
                    if dict_name == 'sub_pre':
                        if key1 in self.sub_dict.keys():
                            dict_num = self.sub_dict[key1]
                    else:
                        if key1 in self.pre_dict.keys():
                            dict_num = self.pre_dict[key1]
                    print("%s\t%d\t" %(key1,dict_num),end = '')
                    save_f.write("%s\t%d\t" %(key1,dict_num))   
                    sys.stdout.flush()
                    for line in sorted_word2:
                        num_pre = 0
                        #if line[0] in names['self.%s_dict.keys()' %dict_name_list[1]]:
                        print('%s:%d' %(line[0],line[1]),end = '\t')
                        save_f.write('%s:%d\t'%(line[0], line[1]))
                        sys.stdout.flush()
                        num += 1
                    print('\n',end = '')
                    save_f.write('\n')
                print("~EOF:")
                save_f.close()

    def identify_sub_pre(self, sub, pre, des,words,arcs):
        for sub_word in sub:
            sub_word_val = sub[sub_word]
            sub_pre_rela = arcs[sub_word_val - 1].relation
            if ("SBV" ==  sub_pre_rela or "ATT" == sub_pre_rela) and arcs[sub_word_val - 1].head in pre.keys():
                res_sub = sub_word
                res_pre = pre[ arcs[sub_word_val - 1].head ]
                #print('des:%s' %des)
                #print('\t'.join(str(i + 1) for i in range(0, len(list(words)))))
                #print('\t'.join(word for word in list(words)))
                #print('\t'.join("%d:%s" % (arc.head, arc.relation) for arc in arcs))
                print("*****real sub pre: %s %s*********" %(res_sub, res_pre))
                sub_pre_name = 'sub_pre'
                pre_sub_name = 'pre_sub'
                names['self.%s_dict'%sub_pre_name] = self.add_dicts(res_sub, res_pre, names['self.%s_dict'%sub_pre_name])
                names['self.%s_dict'%pre_sub_name] = self.add_dicts(res_pre, res_sub, names['self.%s_dict'%pre_sub_name])

    def find_sub_pre_in_dict(self, des):
        words, arcs = ltp_parser.des_parse(des)
        temp_sub = {} #key is word ,val is index
        temp_pre = {} #key is index ,val is word
        for i in range(len(words)):
            if words[i] in self.sub_word_id_dict.keys():
                id_val = self.sub_word_id_dict[words[i]]
                temp_sub[words[i]] = i + 1
                '''
                if words[i] in self.sub_dict.keys():
                    self.sub_dict[words[i]] += 1
                else:
                    self.sub_dict[words[i]] = 1
                '''

            if words[i] in self.pre_word_id_dict.keys():
                temp_pre[i + 1] = words[i]    #self.pre_id_word_dict[id_val]
                '''
                if words[i] in self.pre_dict.keys():
                    self.pre_dict[words[i]] += 1
                else:
                    self.pre_dict[words[i]] = 1
                    '''
        if temp_sub and temp_pre:
            print('---------------------------------------------')
            print(des)
            print('\t'.join(str(i + 1) for i in range(0, len(list(words)))))
            print('\t'.join(word for word in list(words)))
            print('\t'.join("%d:%s" % (arc.head, arc.relation) for arc in arcs))
            print("find sub pre are: %s: %s" %(temp_sub, temp_pre))
            self.identify_sub_pre(temp_sub, temp_pre, des, words, arcs)
        if len(temp_pre) != 0:#add pre dict
            for key,val in temp_pre.items():
                if val in self.pre_dict.keys():
                    self.pre_dict[val] += 1
                else:
                    self.pre_dict[val] = 1
        if len(temp_sub) != 0:
            for key,val in temp_sub.items():
                if key in self.sub_dict.keys():
                    self.sub_dict[key] += 1
                else:
                    self.sub_dict[key] = 1
                    

    def main_function(self, des_dir):
        file_num = len(os.listdir(des_dir))
        count = 0
        for line in os.listdir(des_dir):
            print('start file %d  all file num:%d' %(count,file_num))
            des_path = os.path.join(des_dir,line)
            all_des = codecs.open(des_path, 'r' ,'utf-8')
            for des in all_des:
                des_list = des.split('\t')
                self.find_sub_pre_in_dict(des_list[0])
        sub_pre_name = 'sub_pre'
        pre_sub_name = 'pre_sub'
        self.parse_dict(names['self.%s_dict'%sub_pre_name],'sub_pre')
        self.parse_dict(names['self.%s_dict'%pre_sub_name],'pre_sub')
            
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

if __name__ == '__main__':
    dict_file_dir = '/data/user/licheng/project/app/hospital_guide_robot/backends/nlp_licheng/dict.modify'
    #ori_file_dir = '/data/user/licheng/project/app/hospital_guide_robot/backends/nlp_licheng/ori'
    ori_file_dir = '/data/nlp/corpus.predict_disease/1.ori'
    
    sub_list = ['organ_nlp','tissue_nlp','indicator_nlp','function_nlp','nutrition_nlp']
    pre_list = ['problem_nlp','appearance_nlp']
    
    sp = Sub_Pre(dict_file_dir, sub_list, pre_list)
    sp.main_function(ori_file_dir)    
