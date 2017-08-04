#coding=utf-8

from __future__ import unicode_literals
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from chatterbot.trainers import ListTrainer

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

if __name__ == '__main__':
    cb = ChatterBot()
    while 1:
        try:
            buf = input().rstrip()
        except:
            break
        input_json = [{'user': {}, 'request': {'text': buf, 'type': 0}}]
        response = cb.run(input_json)
        print(response['text'], file = sys.stderr)
