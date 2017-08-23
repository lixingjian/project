#coding=utf-8
'''
from __future__ import unicode_literals
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from chatterbot.trainers import ListTrainer
'''
import json
import urllib
import urllib.request
import sys
sys.path.append('/home/work/xiexueci/project/alg/basic')
import str_util
'''
class ChatterBot:
    def __init__(self):
        self.bot = ChatBot('BOEBot', output_format = 'text')
        self.bot.set_trainer(ChatterBotCorpusTrainer)
        self.bot.train('/data/nlp/corpus.dialog')  # 语料库

    def run(self, req_list):
        response = {'wei': 0, 'text': '', 'type': 0}
        if req_list[-1]['request']['type'] != 0:
            return response
        response['wei'] = 0.1
        response['text'] = self.bot.get_response(req_list[-1]['request']['text']).text
        return response
'''
class ChatterBot:
    def __init__(self):
        self.rule_dict = str_util.read_kv_file('./chat_dict.txt')

    def run(self, req_list):
        response = {'wei': 0, 'text': '', 'type': 0}
        if req_list[-1]['request']['type'] != 0:
            return response
        
        res_wei = 0.1
        query = req_list[-1]['request']['text'].replace('天气', '北京天气')
        if query in self.rule_dict:
            res_text = self.rule_dict[query]
            res_wei = 1
        else:
            url = urllib.parse.quote('http://api.qingyunke.com/api.php?key=free&appid=0&msg=' + query, safe='/:?=&')
            res_json = json.loads(urllib.request.urlopen(url).read().decode('utf-8'), encoding = 'utf-8')
            res_text = res_json['content'].replace('{br}', '\n').replace('菲菲', '导诊机器人')
            if query.find('天气') >= 0 or query.find('笑话') >= 0:
                res_wei = 1
            
        response['wei'] = res_wei
        response['text'] = res_text

        return response

if __name__ == '__main__':
    cb = ChatterBot()
    while 1:
        try:
            buf = input().rstrip()
        except:
            break
        input_json = [{'user': {}, 'request': {'text': buf, 'type': 0}}]
        response = cb.run(input_json)
        print(response, file = sys.stderr)
