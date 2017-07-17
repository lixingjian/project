#coding = utf8
import sys
sys.path.append('../../../alg/basic')
import str_util
from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
import json
from pgmpy.readwrite import BIFReader, BIFWriter, XMLBIFReader, XMLBIFWriter, ProbModelXML, UAIReader, UAIWriter

disease_part = {}
disease_rate = {}
for line in open('disease_intro.json').readlines():
	js = json.loads(line.rstrip())['struct'] 
	disease_rate[js['id']] = js['rate']
	disease_part[js['id']] = js['department']

fea_map = str_util.read_kv_file('models/feature.id')
disease_id = {}
disease_name = {}
ds_rind = {}
for line in open('disease_symptom.json').readlines():
	js = json.loads(line.rstrip())
	id = js['id']
	if not id in disease_rate:
		continue
	disease_name[id] = js['name']
	disease_id[js['name']] = id
	for s, w in js['symptoms'].items():
		if not s in ds_rind:
			ds_rind[s] = {} 
		ds_rind[s][id] = disease_rate[id]

print('init succeed ... type symptoms ...')

while 1:
	try:
		buf = input()
	except:
		break
	a = buf.rstrip().split(' ')
	candidates = {} 
	for sym in a:
		if sym in disease_id:
			id = disease_id[sym]
			if not id in candidates:
				candidates[id] = 0
			candidates[id] += 1	
		if sym in ds_rind:
			for id, rate in ds_rind[sym].items():
				if not id in candidates:
					candidates[id] = 0
				candidates[id] += rate	
	ids = sorted(candidates.items(), key=lambda d:d[1], reverse=True)[:20]
	print('candidates generated')

	dw = {}
	deps = {}
	for i, r in ids:
		if r >= 1:
			for d in disease_part[i]:
				if not d in deps:
					deps[d] = 0
				deps[d] += 1

		try:
			model = BIFReader('models/model.bif.%s' % i).get_model()
		except:
			continue
		infer = VariableElimination(model)
		key = fea_map['D_' + disease_name[i]]
		observed_info = {}
		for sym in a:
			if sym.startswith('SEX_'):
				observed_info['SEX'] = int(sym[len('SEX_'):])
			if sym.startswith('AGE_'):
				observed_info['AGE'] = int(sym[len('AGE_'):])
			sym = 'S_' + sym
			if not sym in model.nodes():
				continue
			if not sym in fea_map:
				continue
			observed_info[fea_map[sym]] = 0
			
		score = infer.query(variables = [key], evidence = observed_info)[key].values[0]
		dw[disease_name[i]] = score
		#print('%s: %s = %.8f' % (i, disease_name[i], score))	

		for d in disease_part[i]:
			if not d in deps:
				deps[d] = 0
			deps[d] += score	
	
	if len(deps) == 0:
		print('unknown symptoms...')
		continue
	
	for name, score in sorted(dw.items(), key=lambda d:d[1], reverse=True)[:10]:
		print('%s\t%.8f' % (name, score))
	
	dep_list = sorted(deps.items(), key=lambda d:d[1], reverse=True)
	print('department: ')
	for dep in dep_list[:3]:
		print(dep)
	
	sys.stdout.flush()	

