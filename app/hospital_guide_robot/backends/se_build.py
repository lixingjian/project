#!usr/bin/env python
# -*- coding: UTF-8 -*-
from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh.analysis import RegexAnalyzer, Tokenizer, Token
import os.path
import json, sys
sys.path.append('../../../lib/nlp/basic')
from se_util import *

class Indexer:
    def __init__(self, fileIndex):
        #self.analyzer = RegexAnalyzer("([\u4e00-\u9fa5])|(\w+(\.?\w+)*)")
        self.analyzer = ChineseAnalyzer()
        self.schema = ChineseSchema()
        if not os.path.exists(fileIndex):
            os.mkdir(fileIndex)
        self.ix = create_in(fileIndex, self.schema)

    def indexAll(self, targetFile, limit):
        doc_id = 1
        self.writer = self.ix.writer()
        for line in open(targetFile, 'r', encoding = 'utf-8').readlines():
            js = json.loads(line, encoding = 'utf-8')
            print('建库中，正在处理第' + str(doc_id) + '页。页面名称：' + js['title'])
            self.writer.add_document(title = js['title'], path = js['url'], content = js['content'])
            doc_id += 1
            if(doc_id > limit and doc_id != 0):
                break
        self.writer.commit()
        print('建库完毕')
    
    def run(self, files):
        for targetFile in files:
            self.indexAll(targetFile, limit = 1e12)

build_dir = './page.build'
input_files = ['./page.xywy.json', './page.guide.json']
a = Indexer(fileIndex = build_dir)
a.run(input_files)
