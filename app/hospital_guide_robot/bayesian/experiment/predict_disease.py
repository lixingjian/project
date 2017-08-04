#coding = utf8
import sys
sys.path.append('../../../alg/basic')
import str_util
from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
import json
from pgmpy.readwrite import BIFReader, BIFWriter, XMLBIFReader, XMLBIFWriter, ProbModelXML, UAIReader, UAIWriter

def age_id(n):
    age_parts = [1, 10, 20, 40, 60]
    for i in range(len(age_parts)):
        if n < age_parts[i]:
            return i
    return len(age_parts)

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

    def extract_self_explain(self, req):
        fea_list = []
        #todo: 利用ac和同义词表，解析出更多表述的症状特征
        for word in req['cont']['req_text'].split(' '):
            sym = 'S_' + word
            if sym in self.fea_map:
                fea_list.append((sym, 0))

        #todo: 抽取部位特征

        return fea_list

    def extract_interactive(self, req_list):
        #todo: 利用机器询问和用户回答，解析出新特征
        return []

    def get_observed_info(self, req_list):
        observed_info = {}
        for fea, val in self.extract_self_explain(req_list[-1]):
            observed_info[self.fea_map[fea]] = val
        for fea, val in self.extract_interactive(req_list):
            observed_info[self.fea_map[fea]] = val
    
        observed_info['SEX'] = req_list[-1]['user']['sex']
        observed_info['AGE'] = age_id(req_list[-1]['user']['age'])

        return observed_info 

    def run(self, input_json):
        if len(input_json) == 0:
            return ''

        req_list = json.loads(input_json, encoding = 'utf-8')
        if len(req_list) == 0:
            return ''
        
        candidates = {} 
        sym_list = req_list[0]['cont']['req_text'].split(' ')
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
            
            
        observed_info = self.get_observed_info(req_list)
        print(observed_info)

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
            
            observed_info_valid = {}
            for k, v in observed_info.items():
                if k in model.nodes():
                    observed_info_valid[k] = v
            score = infer.query(variables = [key], evidence = observed_info_valid)[key].values[0]
            dw[self.disease_name[i]] = score
            #print('%s: %s = %.8f' % (i, self.disease_name[i], score))    

            for d in self.disease_part[i]:
                if not d in deps:
                    deps[d] = 0
                deps[d] += score    
    
        if len(deps) == 0:
            print('unknown symptoms...', file = sys.stderr)
            return ''
    
        for name, score in sorted(dw.items(), key=lambda d:d[1], reverse=True)[:10]:
            print('%s\t%.8f' % (name, score), file = sys.stderr)
    
        dep_list = sorted(deps.items(), key=lambda d:d[1], reverse=True)
        print('department: ', file = sys.stderr)
        for dep, wei in dep_list[:3]:
            print('%s\t%.4f' % (dep, wei), file = sys.stderr)
            req_list[-1]['cont']['res_text'] += '%s ' % dep
        req_list[-1]['cont']['req_wei'] = 100 * dep_list[0][1]         
        return req_list[-1]['cont']['res_text'] 

if __name__ == '__main__':
    d = Diagnosis()
    while 1:
        try:
            buf = input().rstrip()
        except:
            break
        req = {'user': {'sex': 1, 'age': 30}, 'cont': {'req_text': buf, 'req_type': 0, 'res_text': ''}}
        req_list = [req]
        for part in buf.split(' '):
            if part.startswith('age='):
                req['user']['age'] = int(part[len('age='):])
            if part.startswith('sex='):
                req['user']['sex'] = int(part[len('sex='):])
        response = d.run(json.dumps(req_list, ensure_ascii = False))
        print(req_list)
        print(response)
