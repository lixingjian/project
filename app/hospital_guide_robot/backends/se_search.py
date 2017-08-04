#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.analysis import RegexAnalyzer
import os.path
from whoosh.index import open_dir
import json
from se_util import *

class Searching:

    def __init__(self):
        self.analyzer = ChineseAnalyzer()
        self.schema = ChineseSchema() 
        self.ix = open_dir("./page.build", schema = self.schema)
        
    def run(self, data):
        response = {'wei': 0, 'text': '', 'type': 0}
        inputContent = data[-1]['request']['text']
        self.searcher = self.ix.searcher()
        with self.ix.searcher() as searcher:
            self.con = inputContent
            self.result = self.searcher.find('title', self.con)
            print(len(self.result), file = sys.stderr)
            
            final_queue = sorted(self.result[:20], key = lambda d:len(d['content']))
            ret = resort(inputContent, final_queue)
            if len(ret) > 0:
                article, wei = ret[0]
                response['wei'] = wei
                response['text'] = article['title'] + '\n'+ article['content']
            return response

if __name__ == '__main__':
    h = Searching()
    while 1:
        try:
            buf = input().rstrip()
        except:
            break
        input_json = [{'user': {}, 'request': {'text': buf}}]
        ret = h.run(input_json)
        print(ret)
