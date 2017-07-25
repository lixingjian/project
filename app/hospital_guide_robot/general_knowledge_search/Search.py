#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.analysis import RegexAnalyzer
import os.path
from whoosh.index import open_dir
import json
class Searching:

    def __init__(self):
        self.analyzer = RegexAnalyzer("([\u4e00-\u9fa5])|(\w+(\.?\w+)*)")
        self.schema = Schema(title=TEXT(stored=True, analyzer=self.analyzer), path=ID(stored=True), content=TEXT(stored=True, analyzer=self.analyzer))
        self.ix = open_dir("/home/work/github/project/app/hospital_guide_robot/general_knowledge_search/tmp/")
        

    def testRun(self):
        self.searcher = self.ix.searcher()
        while 1:
            with self.ix.searcher() as searcher:
                self.con = input('Search:')
                self.results =self.searcher.find('title', self.con)
            print(self.results[0:5])
            print('xiayige')
            print(self.results[0]['content'])
    
    def getExecutiveLevel(self):
        if self.result != []:
            terms = self.con.split()
            res = self.results[0]['content'].split()
            ts = 0
            tn = len(terms)
            for i in terms:
                tmps = 0
                for j in res:
                   if i == j:
                        tmps += 1
                tmps = tmps/len(res)
                ts += tmps
            ts = ts/tn
            self.score = (ts*0.2)+0.5
            return self.score
        else:
            return 0
    
    def run(self, jsData):
        data = json.loads(jsData)
        inputContent = data['Self Explaination']
        with self.ix.searcher() as searcher:
            self.con = inputContent
            self.result = self.searcher.find('title', self.con)
            returnFile = json.dumps(self.result[0:10], ensure_ascii = False)
            self.outputContent = self.result
            return returnFile

        

