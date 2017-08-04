# -*- coding: utf-8 -*-
from pyltp import Segmentor
from pyltp import Postagger
from pyltp import NamedEntityRecognizer
from pyltp import Parser

class LexParser:
    def __init__(self, dictdir, use_pos = True, use_ner = True, use_parser = True):
        self.use_pos = use_pos
        self.use_ner = use_ner
        self.use_parser = use_parser

        self.segmentor = Segmentor()
        self.segmentor.load_with_lexicon(dictdir + '/cws.model', dictdir + '/wordlist.custom')
        
        if self.use_pos:
            self.postagger = Postagger() # 初始化实例
            self.postagger.load(dictdir + '/pos.model')  # 加载模型
        if self.use_ner:
            self.recognizer = NamedEntityRecognizer() # 初始化实例
            self.recognizer.load(dictdir + '/ner.model')  # 加载模型
        if self.use_parser:
            self.parser = Parser() # 初始化实例
            self.parser.load(dictdir + '/parser.model')  # 加载模型

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
        ret = lex.run(buf)
        nw = len(ret[0])
        for i in range(nw):
            print('%s/%s/%s/%d:%s\t' % (ret[0][i], ret[1][i], ret[2][i], ret[3][i].head, ret[3][i].relation))
        print('')
    
