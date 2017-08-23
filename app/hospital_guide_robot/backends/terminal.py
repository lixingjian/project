import sys, os, json, random
import copy
from predict_disease import Diagnosis  
from se_search import Searching 
from chatter_bot import ChatterBot

request_template = {
        'user' : {
            'uid' : 1,      #int, (0, 9999999) APP通过声纹或人脸识别确定
            'name': '',     #string, 通过触摸屏填充、身份证读取等方式读入
            'sex' : 0,      #int, [0 / 1] 0：女，1：男
            'age' : 10      #int, (0, 150) 通过触摸屏填充、身份证读取等方式确定
        }, 
        'request' : {
            'serv' : 0,     #int, [0, 9] 请求哪个服务，0：用户未选择，1：分诊，2：指南，3：聊天
            'text' : '',    #string, 通过语音识别或触屏选择得到的输入文字
            'type' : 0,     #int, [0, 255] 请求类型，0：语音识别，1：触屏选择
            'time' : 0     #int, server返回的请求时间
        } 
    }        
response_template = {
        'text' : '', #string, server返回的文字内容 
        'type' : 0,  #int, [0, 255] 回复类型：0：聊天回复，1：指南回复，2：分诊回复，3：分诊交互
        'wei' : 0,  #float, [0, 1] 回复置信度
        'time' : 0  #int, server返回的请求时间
    }


multi_interactive = False
class Terminal:
    def __init__(self):
        self.history = {}
        self.serv_list = [Diagnosis(), Searching(), ChatterBot()]

    def question_wei(self, q):
        wei_list = [0, 1, 1]
        if (q.find('挂') > 0 or q.find('看') > 0) and q.find('科') > 0:
            wei_list = [1, 0, 0]
        if q.find('我想') > 0 or q.find('我要') > 0 or q.find('在哪') > 0 or q.find('怎么走') > 0:
            wei_list = [0, 1, 0]
        return wei_list

    def run(self, request):
        if len(request['request']['text']) < 2:
            return copy.deepcopy(response_template)

        uid = request['user']['uid']
        if not uid in self.history:
            self.history[uid] = []
        self.history[uid].append([request, None])
        
        req_list = []
        if multi_interactive:
            for req, res in self.history[uid]:
                req_list.append(req)
        else:
            req_list.append(request)

        candidates = []
        for i in range(len(self.serv_list)):
            serv = self.serv_list[i]
            res = serv.run(req_list)
            res['src'] = i
            res['wei'] *= self.question_wei(req_list[0]['request']['text'])[i]
            candidates.append(res)
            print(res)

        response = sorted(candidates, key=lambda d:d['wei'], reverse=True)[0]
        if len(self.history[uid]) > 3:    
            self.history[uid].pop(0)
        self.history[uid][-1][1] = response
        return response

'''
def fake_input(buf, uid = 0):
    request = copy.deepcopy(request_template)
    user_info = request['user']
    if uid == 0:
        user_info['uid'], user_info['name'], user_info['sex'], user_info['age'] = random.choice(user_list)
    else:
        user_info['uid'], user_info['name'], user_info['sex'], user_info['age'] = user_list[uid - 1]
    request['request']['text'] = buf.strip()
    request['request']['type'] = 0
    return request

sex_str = ['女', '男']
user_list = [(1, 'Tom', 1, 2), (2, 'Bill', 1, 65), (3, 'Lucy', 0, 28)]
t = Terminal()
uid = random.randint(0, 2)
iters = random.randint(1, 5)

while 1:
    try:
        buf = input().rstrip()
    except:
        break
    if iters == 0:
        uid = random.randint(0, 2)
        iters = random.randint(1, 5)
    request = fake_input(buf, uid)    
    print(request)
    res = t.run(request)['text']
    print('response: ' + res)
    iters -= 1
'''    
