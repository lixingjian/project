# -*- coding: utf-8 -*-

import codecs
import os
import sys

LTP_DATA_DIR = '/home/chenlee/documents/mywork/BOE/ltp_data'#'/Users/Herman/Documents/BOE/pyltp/ltp_data' # Modify this dir
cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')
pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')
par_model_path = os.path.join(LTP_DATA_DIR, 'parser.model')
# Modify this dir to where all_nlp is
# You may run createAll.py in a folder with all input nlp files to obtain
# all_nlp
LEXICON_PATH = 'all_nlp'

from pyltp import Segmentor
from pyltp import Postagger
from pyltp import Parser

class LTP_parse:
    def __init__(self):
        self.segmentor = Segmentor()
        self.segmentor.load_with_lexicon(cws_model_path, LEXICON_PATH)
        self.postagger = Postagger()
        self.postagger.load(pos_model_path)
        self.parser = Parser()
        self.parser.load(par_model_path)

    def des_parse(self, description):
        words = self.segmentor.segment(description)
        postags = self.postagger.postag(words)
        arcs = self.parser.parse(words, postags)
        '''
        print('\t'.join(str(i + 1) for i in range(0, len(list(words)))))
        print('\t'.join(word for word in list(words)))
        print('\t'.join("%d:%s" % (arc.head, arc.relation) for arc in arcs))
        '''
        return words, arcs
if __name__ == '__main__':
    lp = LTP_parse()
    des = input(':')
    lp.des_parse(des)
