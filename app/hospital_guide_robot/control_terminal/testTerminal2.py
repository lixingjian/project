import sys, os, json, random
import copy
from testServer import *

user_list = [('Tom', '男', '婴儿'), ('Bill', '男', '老年'), ('Lucy', '女', '青年')]
serv_list = [testChat, testGuide, testDiagnose]

def fake_input(buf, uid = ''):
	request = {}
	if uid == '':
		request['id'], request['sex'], request['age'] = random.choice(user_list)
	else:
		request['id'], request['sex'], request['age'] = user_list[uid]
	request['text'] = buf.strip()
	request['time'] = 'y-m-d'
	return request

class Terminal:
	def __init__(self):
		self.history = {}

	def run(self, request):
		uid = request['id']
		if not uid in self.history:
			self.history[uid] = []
		elif len(self.history[uid]) > 3:	
			self.history[uid].pop()
		new_record = {'request': copy.deepcopy(request), 'response': {}}
		self.history[uid].insert(0, new_record)
		
		print(self.history[uid])
		candidates = []
		for serv in serv_list:
			res = serv(json.dumps(self.history[uid], ensure_ascii = False))
			candidates.append(res)
		
		response = sorted(candidates, key=lambda d:d['weight'], reverse=True)[0]
		new_record['response'] = response
		return response

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
	res = t.run(request)['text']
	print('response: ' + res)
	iters -= 1
