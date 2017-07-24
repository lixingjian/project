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
                con = input('Search:')
                self.results =self.searcher.find('title', con)
            print(self.results[0:5])
            print('xiayige')
            print(self.results[0]['content'])
    
    def getExecutiveLevel(self):
        return

s = Searching()
s.testRun()

