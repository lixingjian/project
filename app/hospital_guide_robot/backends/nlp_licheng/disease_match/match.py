# -*- coding: utf-8 -*-

import codecs
import sys
import os
import itertools
import time
sys.path.append('/data/user/licheng/project/app/hospital_guide_robot/dialog_frame')
from symp_extractor import SympExtractor

class DiseaseMatch:
    def __init__(self):
        self.dicts = {}
        self.reverse_dicts = {} 
        self.se = SympExtractor()

    def add_dicts(self,key1,key2,dicts):                
        if key1 in dicts.keys() and key2 in dicts[key1].keys():
            dicts[key1][key2] += 1 
        if key1 in dicts.keys() and key2 not in dicts[key1].keys():              
            dicts[key1].update({key2:1})
        if key1 not in dicts.keys():                           
            dicts.update({key1:{key2:1}})
        return dicts

    def find_disease(self,des):
        res = self.se.parse(des)
        if len(res) == 0 or len(res) == 1:
            return False
        disease_list = []
        for ele in res:
            disease_list.append(ele['name'])
        return disease_list

    def parse_list_add_dicts(self,dis_list,dicts):
        for ele in dis_list:
            temp = dis_list
            temp.remove(ele)
            for ele_in in temp:
                dicts = self.add_dicts(ele,ele_in,dicts)
        return dicts
        
    def dicts_reverse(self,dicts):
        reverse_dicts = {}
        #for every key2 
        for key1,key2_val in dicts.items():
            for key2, val in key2_val.items():
                #inner loop if key2 in key2_val_in 
                for key1_in, key2_val_in in dicts.items():
                    if key2 in key2_val_in.keys():
                        reverse_dicts = self.add_dicts(key2,key1_in,reverse_dicts)
        return reverse_dicts

    def n_same_disease(self,keys,n):
        disease = []
        dicts = {}
        for ele in keys:
            for key2,val in self.reverse_dicts[ele].items():
                if key2 in dicts.keys():
                    dicts[key2] += 1
                else:
                    dicts[key2] = 1
        for key, val in dicts.items():
            if val == n:
                disease.append(key)
        if len(disease) == 0 or len(disease) == 1:
            return False
        return disease

    #define a function used to determine if there are n same diseases,then put them together
    '''
    对reverse_dicts进行组合，即从reverse_dicts中随机取出n个键-值进行组合，对于每个组合，比如：
    {key1:{key1_1:val1_1,key1_2:val1_2,…}}，
    {key2:{key2_1:val2_1,key2_2:val2_2,…}}，
    {key3:{key3_1:val3_1,key3_2:val3_2,…}}，
    若内部词典中还有同名的疾病，比如key1_1 = key2_1 = key3_1，key1_2 = key2_2 = key3_2，则将key1_1与key1_2聚为一类。
    '''
    def first_cluster(self,dicts,n):
        #use combinations function
        cluster_f = open('cluster_res','w')
        for ele_key in itertools.combinations(dicts, n):
            disease = self.n_same_disease(ele_key, n)
            if disease:
                print()
                for ele in disease:
                    print('%s\t'%ele,end='')
                    cluster_f.write('%s\t'%ele)
                    sys.stdout.flush()
                    for ele1 in ele_key:
                        print('%s:%d' %(ele1,self.dicts[ele][ele1]),end = '\t')
                        cluster_f.write('%s:%d' %(ele1,self.dicts[ele][ele1]))
                        sys.stdout.flush()
                    print()
                    cluster_f.write('\n')
                print()
                cluster_f.write('\n')
 
    def main_function(self,des_dir):
        #read file data,put them in self.dicts
        dicts = {}
        line_nums = 10185447
        line_num = 0
        time1 = time.time()
        for ele in os.listdir(des_dir):
            des_path = os.path.join(des_dir, ele)
            des_file = codecs.open(des_path, 'r' , 'utf-8')
            for des in des_file:
                line_num += 1
                if line_num % 100000 == 0:
                    print('complete:%f' %(line_num/line_nums))
                res_des = des.split('\t')[0]
                disease_list = self.find_disease(res_des)
                if disease_list == False:
                    continue
                #print('discriber:%s' %res_des)
                #print('qualified:%s' %disease_list)
                dicts = self.parse_list_add_dicts(disease_list,dicts)
        self.dicts = dicts
        self.print_dicts(self.dicts,'dicts')
        #reverse dicts
        self.reverse_dicts = self.dicts_reverse(self.dicts)
        self.print_dicts(self.reverse_dicts,'reverse_dicts')
        time2 = time.time()
        print('time2:%f' %(time2 - time1))
        #first cluster
        self.first_cluster(self.reverse_dicts,2)
        time3 = time.time()
        print('time3:%f' %(time3 - time2))
    
    def print_dicts(self,dicts,name):
        print(name)
        #res_f = open(name,'w')
        for ele in dicts.items():
            print(ele)
            #res_f.write('%s' %ele)
        #res_f.close()

if __name__ == '__main__':
   dm = DiseaseMatch()
   ori_file_dir = '/data/nlp/corpus.predict_disease/1.ori'
   ori_file_dir_test = '/data/user/licheng/project/app/hospital_guide_robot/backends/nlp_licheng/ori'
   dm.main_function(ori_file_dir)
   #dicts = {'a':{'a1':1,'a2':2},'b':{'a1':1,'b2':2},'c':{'a1':1,'b1':2}}
   #dm.cluster_init(dicts,3)
   #print(dicts)
   #reve = dm.dicts_reverse(dicts)
   #print(reve)qa       
