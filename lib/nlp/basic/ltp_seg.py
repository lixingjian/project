# -*- coding: utf-8 -*-
from pyltp import Segmentor
from pyltp import Postagger
from pyltp import NamedEntityRecognizer
from pyltp import Parser
import numpy as np
import sys
sys.path.append('../../../alg/basic')
import str_util

class LexParser:
    def __init__(self, dictdir, use_pos = True, use_ner = True, use_parser = True):
        self.use_pos = use_pos
        self.use_ner = use_ner
        self.use_parser = use_parser

        dict_custom = dictdir + '.custom'
        self.segmentor = Segmentor()
        self.segmentor.load_with_lexicon(dictdir + '/cws.model', dict_custom + '/word_new.txt')
        
        if self.use_pos:
            self.postagger = Postagger() # 初始化实例
            self.postagger.load(dictdir + '/pos.model')  # 加载模型
        if self.use_ner:
            self.recognizer = NamedEntityRecognizer() # 初始化实例
            self.recognizer.load(dictdir + '/ner.model')  # 加载模型
        if self.use_parser:
            self.parser = Parser() # 初始化实例
            self.parser.load(dictdir + '/parser.model')  # 加载模型

        dict_custom = dictdir + '.custom'
        self.word_freq = str_util.read_kv_file(dict_custom + '/word_freq.txt', value_type = 'float')
        self.word_syn = str_util.read_kv_file(dict_custom + '/word_syn.txt', value_type = 'float')
        self.word_stop = str_util.read_kv_file(dict_custom + '/word_stop.txt', read_value = False)

    def run(self, buf):
        ret = []
        words = self.segmentor.segment(buf)
        ret.append(words)
        if self.use_pos:
            postags = self.postagger.postag(words)  # 词性标注
            ret.append(postags)
        if self.use_ner:
            netags = self.recognizer.recognize(words, postags)  # 命名实体识别
            ret.append(netags)
        if self.use_parser:    
            arcs = self.parser.parse(words, postags)  # 句法分析
            ret.append(arcs)
        return ret    

    def sim(self, p1, p2):
        word_wei = [[], []]
        for i in range(2):
            wlist = [p1, p2][i]
            for word in wlist:
                wei = 1
                if word in self.word_stop:
                    wei = 0
                elif word in self.word_freq:
                    wei = 50 / (1 + self.word_freq[word])
                word_wei[i].append([word, wei])
        
        match_wei = 0
        for word1, wei1 in word_wei[0]:
            for word2, wei2 in word_wei[1]:
                if word1 == word2 or ('%s,%s' % (word1, word2)) in self.word_syn:
                    match_wei += 0.5 * (wei1 + wei2)
                    #print('match\t%s(%f)\t%s(%f)\t%f' % (word1, wei1, word2, wei2, match_wei), file = sys.stderr)
                    break
        
        total_wei = 0.5 * (sum([y for x,y in word_wei[0]]) + sum([y for x,y in word_wei[1]]))
        score = match_wei / (1e-8 + total_wei)
        if score > 1:
            score = 1
        
        print(match_wei, total_wei)

        return score

    def __del__(self):
        self.segmentor.release()
        if self.use_pos:
            self.postagger.release()  # 释放模型
        if self.use_ner:
            self.recognizer.release()  # 释放模型
        if self.use_parser:
            self.parser.release()  # 释放模型

lex = LexParser('/data/nlp/ltp_data')
if __name__ == '__main__':
    while 1:
        try:
            buf = input().rstrip()
        except:
            break
        a = buf.split('\t')
        s1 = a[0]
        s2 = a[1]
        ret = lex.run(s1)
        nw = len(ret[0])
        for i in range(nw):
            print('%s/%s/%s/%d:%s\t' % (ret[0][i], ret[1][i], ret[2][i], ret[3][i].head, ret[3][i].relation))
        print('')
        ret2 = lex.run(s2)
        nw = len(ret2[0])
        for i in range(nw):
            print('%s/%s/%s/%d:%s\t' % (ret2[0][i], ret2[1][i], ret2[2][i], ret2[3][i].head, ret2[3][i].relation))
        print('')
        score = lex.sim(ret[0], ret2[0])
        print('sim\t%s\t%s\t%f' % (s1, s2, score))
