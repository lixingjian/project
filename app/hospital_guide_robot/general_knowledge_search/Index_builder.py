#!usr/bin/env python
# -*- coding: UTF-8 -*-
from whoosh.index import create_in
from whoosh.fields import *
from whoosh.analysis import RegexAnalyzer
from whoosh.index import open_dir
import os.path
import json
class Indexer:
    def __init__(self, fileIndex,targetFile):
        self.analyzer = RegexAnalyzer("([\u4e00-\u9fa5])|(\w+(\.?\w+)*)")
        self.schema = Schema(title=TEXT(stored=True, analyzer = self.analyzer), path=ID(stored=True), content=TEXT(stored=True, analyzer = self.analyzer))
        if not os.path.exists(fileIndex):
            os.mkdir(fileIndex)
        self.ix = create_in(fileIndex, self.schema)
        self.targetFile = targetFile

    def indexAll(self, targetFile, limit):
        doc_id = 1
        self.writer = self.ix.writer()
        for line in open(self.targetFile, 'r', encoding = 'utf-8').readlines():
            js = json.loads(line, encoding = 'utf-8')
            print('建库中，正在处理第' + str(doc_id) + '页。页面名称：' + js['title'])
            self.writer.add_document(title = js['title'], path = js['url'], content = js['content'])
            doc_id += 1
            if(doc_id > limit and doc_id != 0):
                break
        self.writer.commit()
        print('建库完毕')
    
    def run(self):
        #self.init(fileIndex = input('请输入建库或已存在库路径：'), targetFile = input('请输入数据文件名称'))
        self.indexAll(self.targetFile, limit = int(input('请输入入库文件数上限（无上限请输入0）：')))

a = Indexer(fileIndex = input('请输入建库或已存在库路径：'), targetFile = input('请输入数据文件名称'))
a.run()
