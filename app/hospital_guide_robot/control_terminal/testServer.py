import sys, random, json
sys.path.append('../bayesian')
from predict_disease import Diagnosis

chat_keys = ['好', '吗', '你']
def testChat(request):
	response = {'text': '', 'weight': 0, 'type': 'normal'}
	js = json.loads(request, encoding = 'utf-8')
	for key in chat_keys:
		if js[0]['request']['text'].find(key) >= 0:
			response['text'] = '你好，我是聊天服务'
			response['weight'] = 0.6
	return response		

guide_keys = ['在哪', '怎么走', '位置']
def testGuide(request):
	response = {'text': '', 'weight': 0, 'type': 'normal'}
	js = json.loads(request, encoding = 'utf-8')
	for key in guide_keys:
		if js[0]['request']['text'].find(key) >= 0:
			response['text'] = '在%d楼大厅' % random.randint(1, 9)
			response['weight'] = 0.6
	return response		

d = Diagnosis()
diag_keys = ['疼', '痛', '痒', '头', '耳', '鼻', '眼', '嘴', '肚', '腿']
res_list = ['挂号外科', '挂号内科', '请问是否发烧']
def testDiagnose(request):
	response = d.run(request)
	return response		
'''	
	response = {'text': '', 'weight': 0, 'type': 'normal'}
	js = json.loads(request, encoding = 'utf-8')
	if len(js) > 1 and js[1]['response']['type'] == 'clarify':
		response['text'] = random.choice(res_list[:2])
		response['weight'] = 1
		return response

	for key in diag_keys:
		if js[0]['request']['text'].find(key) >= 0:
			text = random.choice(res_list)
			response['text'] = text
			response['weight'] = 1
			if text.find('请问') >= 0:
				response['type'] = 'clarify'
	return response		
'''
