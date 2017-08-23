#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.analysis import RegexAnalyzer
import os.path
from whoosh.index import open_dir
from whoosh import qparser
from whoosh.qparser import QueryParser
import json
from se_util import *
import ahocorasick

class Guide:
    def __init__(self):
        self.key_dict = ahocorasick.Automaton()
        self.position_dict = str_util.read_kv_file('./guide_dict.txt')
        for line in open('./guide_dict.txt').readlines():
            a = line.rstrip().split('\t')
            if len(a) != 2:
                print('Error: invalid line: %s' % line)
                continue
            for key in [a[0], a[1]]:
                self.key_dict.add_word(key, (len(self.key_dict), key))
        self.key_dict.make_automaton()

    def get_position(self, query):
        keylist = ['我想', '我要', '哪', '什么地方', '什么位置', '什么方位']
        valid = False
        for key in keylist:
            if query.find(key) >= 0:
                valid = True
                break
        if not valid:
            return ''

        ret = {}
        for end_idx, item in self.key_dict.iter(query):
            key = item[1]
            begin_idx = end_idx - len(key)
            if not key in self.position_dict:
                continue
            val = self.position_dict[key]
            ret[val] = 1
        
        if len(ret) == 1:
            return 'LOC_' + list(ret.keys())[0]
        
        return 'UNKNOWN'


class Searching:

    def __init__(self):
        self.analyzer = ChineseAnalyzer()
        self.schema = ChineseSchema() 
        self.ix = open_dir("./page.build", schema = self.schema)
        self.guider = Guide()

    def run(self, data):
        response = {'wei': 0, 'text': '', 'type': 0}
        inputContent = data[-1]['request']['text'].lower()
        position = self.guider.get_position(inputContent)
        if position != '':
            response['wei'] = 1
            response['type'] = 0
            response['text'] = position
            return response

        self.searcher = self.ix.searcher()
        with self.ix.searcher() as searcher:
            self.con = inputContent

            og = qparser.OrGroup.factory(0.9)
            parser = qparser.QueryParser('title', self.schema, group = og)
            query = parser.parse(self.con)
            self.result = self.searcher.search(query)

            #self.result = self.searcher.find('title', self.con)
            print(len(self.result), file = sys.stderr)
            
            final_queue = sorted(self.result[:20], key = lambda d:len(d['content']))
            ret = resort(inputContent, final_queue)
            for article, wei in ret[:5]:
                print('%s\t%f' % (article['title'], wei), file = sys.stderr)

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
