#coding = utf8
import sys
sys.path.append('../../../alg/basic')
import str_util
from pgmpy.models import BayesianModel
from pgmpy.factors import TabularCPD
from pgmpy.inference import VariableElimination
import json
from pgmpy.readwrite import BIFReader, BIFWriter, XMLBIFReader, XMLBIFWriter, ProbModelXML, UAIReader, UAIWriter

def age_id(n):
    age_parts = [1, 10, 20, 40, 60]
	for i in range(len(age_parts)):
		if n < age_parts[i]:
			return i
	return len(age_parts)

def sex_id(s):
	if s == '女':
		return 0
	return 1

class Diagnosis:
	def __init__(self):
		self.disease_part = {}
		self.disease_rate = {}
		for line in open('disease_intro.json').readlines():
			js = json.loads(line.rstrip())['struct'] 
			self.disease_rate[js['id']] = js['rate']
			self.disease_part[js['id']] = js['department']

		self.fea_map = str_util.read_kv_file('models/feature.id')
		self.disease_id = {}
		self.disease_name = {}
		self.ds_rind = {}
		for line in open('disease_symptom.json').readlines():
			js = json.loads(line.rstrip())
			id = js['id']
			if not id in self.disease_rate:
				continue
			self.disease_name[id] = js['name']
			self.disease_id[js['name']] = id
			for s, w in js['symptoms'].items():
				if not s in self.ds_rind:
					self.ds_rind[s] = {} 
				self.ds_rind[s][id] = self.disease_rate[id]

		print('init succeed ... type symptoms ...', file = sys.stderr)

	def run(self, request):
		response = {'text': '', 'weight': 0, 'type': 'normal'}
		js = json.loads(request, encoding = 'utf-8')
		if len(js) == 0:
			return response
		
		candidates = {} 
		sym_list = js['Self Explanation'].split(' ')
		for sym in sym_list:
			if sym in self.disease_id:
				id = self.disease_id[sym]
				if not id in candidates:
					candidates[id] = 0
				candidates[id] += 1	
			if sym in self.ds_rind:
				for id, rate in self.ds_rind[sym].items():
					if not id in candidates:
						candidates[id] = 0
					candidates[id] += rate	
		ids = sorted(candidates.items(), key=lambda d:d[1], reverse=True)[:20]
		print('candidates generated', file = sys.stderr)

		dw = {}
		deps = {}
		for i, r in ids:
			if r >= 1:
				for d in self.disease_part[i]:
					if not d in deps:
						deps[d] = 0
					deps[d] += 1

			try:
				model = BIFReader('models/model.bif.%s' % i).get_model()
			except:
				continue
			infer = VariableElimination(model)
			key = self.fea_map['D_' + self.disease_name[i]]
			observed_info = {}
			if 'sex' in js[0]['User Info']:
				observed_info['SEX'] = js['User Info']['sex']
			if 'age' in js[0]['User Info']:
				observed_info['AGE'] = js['User Info']['age']

			for sym in sym_list:
				sym = 'S_' + sym
				if not sym in model.nodes():
					continue
				if not sym in self.fea_map:
					continue
				observed_info[self.fea_map[sym]] = 0
			
			score = infer.query(variables = [key], evidence = observed_info)[key].values[0]
			dw[self.disease_name[i]] = score
			#print('%s: %s = %.8f' % (i, self.disease_name[i], score))	

			for d in self.disease_part[i]:
				if not d in deps:
					deps[d] = 0
				deps[d] += score	
	
		if len(deps) == 0:
			print('unknown symptoms...', file = sys.stderr)
			return response
	
		for name, score in sorted(dw.items(), key=lambda d:d[1], reverse=True)[:10]:
			print('%s\t%.8f' % (name, score), file = sys.stderr)
	
		dep_list = sorted(deps.items(), key=lambda d:d[1], reverse=True)
		print('department: ', file = sys.stderr)
		for dep, wei in dep_list[:3]:
			print(dep, file = sys.stderr)
			response['text'] += dep
			response['text'] += ' '
		response['weight'] = 1000 * dep_list[0][1] 		
		return response	

if __name__ == '__main__':
	d = Diagnosis()
	while 1:
		try:
			buf = input().rstrip()
		except:
			break
		request = [{'request': {'text': buf}}]
		for part in buf.split(' '):
			if part.startswith('age='):
				request[0]['request']['age'] = age_id(int(part[len('age='):]))
			if part.startswith('sex='):
				request[0]['request']['sex'] = sex_id(part[len('sex='):])
		response = d.run(json.dumps(request, ensure_ascii = False))
		print(request)
		print(response)
