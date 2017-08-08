#!usr/bin/env python
# -*- coding: UTF-8 -*-
from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh.analysis import RegexAnalyzer, Tokenizer, Token
import os.path
import json, sys, math
sys.path.append('../../../alg/basic')
sys.path.append('../../../lib/nlp/basic')
import str_util
from ltp_seg import LexParser

lex = LexParser('/data/nlp/ltp_data', use_ner = False, use_parser = False)
class ChineseTokenizer(Tokenizer):
    def __call__(self, value, positions = False, chars = False, keeporiginal = False, removestops = True,  
                start_pos = 0, start_char = 0, mode = '', **kwargs):  
        assert isinstance(value, text_type), "%r is not unicode" % value  
        t = Token(positions, chars, removestops = removestops, mode = mode, **kwargs)
        seg_ret = lex.run(value)
        for w in seg_ret[0]:
            t.original = t.text = w  
            t.boost = 1.0
            if positions:
                t.pos = start_pos + value.find(w)  
            if chars:  
                t.startchar = start_char + value.find(w)  
                t.endchar = start_char + value.find(w) + len(w)  
            yield t  

def ChineseAnalyzer():  
    return ChineseTokenizer()  

def ChineseSchema():
    aly = ChineseAnalyzer()
    return Schema(title = TEXT(stored = True, analyzer = aly),
                 path=ID(stored = True),
                 content = TEXT(stored = True))

def resort(query, res_list):
    ret_list = []
    for article in res_list:
        title = article['title'].split('_')[0]
        
        wlist1 = lex.run(query)[0]
        wlist2 = lex.run(title)[0]
        qt_match_score = lex.sim(wlist1, wlist2)
        
        doc_len_score = 1
        m = len(article['content'])
        if m > 50:
            doc_len_score /= math.log10(m / 5)  #优先展现较短的文章

        wei = qt_match_score * doc_len_score
        
        ret_list.append((article, wei))
    return sorted(ret_list, key = lambda d:d[1], reverse = True)
