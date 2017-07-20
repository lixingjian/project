#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from whoosh.index import create_in
from whoosh.fields import *
from whoosh. analysis import RegexAnalyzer

class Searching:

    def __init__(self):
        self.analyzer = RegexAnalyzer(u"([\u4e00-\u9fa5])")
        self.schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT(stored=True, analyzer=self.analyzer))
        self.ix = create_in("/home/work/github/project/app/hospital_guide_robot/general_knowledge_search/temp/", self.schema)
        self.writer = self.ix.writer()

    def indexContent(self, inputContent):
        self.writer.add_document(title = inputContent['title'], path = inputContent['url'], content = inputContent['content'])
        self.writer.commit()

    def testRun(self):
        doc1 = {'title' : '知道了', 'url' : 'www.healthcare.gov/medicalinsurancenow', 'content' : '医保真好'} 
        doc2 = {'title' : '肝功能网', 'url' : 'www.healthcare.gov/Indianahugeasscunt', 'content' : '开机车'}
        doc3 = {'title' : '印度了怎么办', 'url' : 'www.healthcare.gov/indiancunt', 'content' : '酱紫啊'}
        doc4 = {'title' : '摩托车', 'url' : 'www.healthcare.gov/porche', 'content' : '买不起porche'}

        self.searcher = self.ix.searcher()
        results =selaf.searcher.find('content', '开机车')
        print(result)


s = Searching()
s.testRun()

