# -*- coding: utf-8 -*-

"""
Created: Aug 1, 2017
Author: Haozhe
updata by Chenlee

This file extacts the keywords from a patient's description and prints
out the corresponding expressions stored in our dictionary


NOTE: Use Python 3.5 to run
"""
import sys
import ahocorasick
import json
import codecs

class Match:
    def __init__(self):
        self.ac = ahocorasick.Automaton()

    #load the word and put it in ahocorasick
    def load(self, file_dir):
        result = []
        input_data = codecs.open(file_dir, 'r', 'utf-8')
        for line in input_data:
            line_list = line.split()
            for line in line_list:
                self.ac.add_word(line, (len(self.ac),line))

    #return a tuple  (字符中出现的位置,(键值，匹配的字符串))
    def match(self, description):
        self.ac.make_automaton()
        return self.match_max_len(self.ac.iter(description))    
    
    #match max len words
    def match_max_len(self, ac_result):
        ret = []
        for end_idx, (wid, word) in sorted(ac_result, key = lambda d:len(d[1][1]), reverse = True):
            begin_idx = end_idx - len(word)
            valid = True
            for e, (_, w) in ret:
                b = e - len(w)
                if (begin_idx >= b and begin_idx < e) or (end_idx > b and end_idx <= e):
                    valid = False
                    break
            if not valid:
                continue
            ret.append((end_idx, (wid, word)))
        return ret

if __name__ == '__main__':
    path = '/data/user/lixingjian/data/dict'
    matcher = Match()
    matcher.load('/data/user/lixingjian/data/dict/organ_nlp')
    matcher.load('/data/user/lixingjian/data/dict/tissue_nlp')
    description = input(u'input:')
    print(matcher.match(description))
