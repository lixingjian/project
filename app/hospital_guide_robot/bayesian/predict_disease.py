#coding = utf8
import sys
sys.path.append('../../../alg/basic')
import str_util
from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
import json
from pgmpy.readwrite import BIFReader, BIFWriter, XMLBIFReader, XMLBIFWriter, ProbModelXML, UAIReader, UAIWriter

fea_map = str_util.read_kv_file('models/feature.id')
disease_name = {}
ds_rind = {}
for line in open('disease_symptom.json').readlines():
	js = json.loads(line.rstrip())
	id = js['id']
	disease_name[id] = js['name']
	for s, w in js['symptoms'].items():
		if not s in ds_rind:
			ds_rind[s] = set([])
		ds_rind[s].add(id)	

while 1:
	try:
		buf = input()
	except:
		break
	a = buf.rstrip().split(' ')
	ids = set([])
	for sym in a:
		if sym in ds_rind:
			ids = ids.union(ds_rind[sym])
	
	dw = {}
	for i in ids:
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
		print('%s: %s = %.8f' % (i, disease_name[i], score))	
	
	for name, score in sorted(dw.items(), key=lambda d:d[1], reverse=True)[:10]:
		print('%s\t%.8f' % (name, score))
	sys.stdout.flush()	

