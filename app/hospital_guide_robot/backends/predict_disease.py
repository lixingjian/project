#coding = utf8
import sys
sys.path.append('../../../alg/basic')
import str_util
from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
import json
from pgmpy.readwrite import BIFReader, BIFWriter, XMLBIFReader, XMLBIFWriter, ProbModelXML, UAIReader, UAIWriter
import ahocorasick

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
        self.symptom_dict = ahocorasick.Automaton()
        for line in open('disease_symptom.json').readlines():
            js = json.loads(line.rstrip())
            id = js['id']
            if not id in self.disease_rate:
                continue
            self.disease_name[id] = js['name']
            self.disease_id[js['name']] = id
            for s, w in js['symptoms'].items():
                if not s in self.symptom_dict:
                    self.symptom_dict.add_word(s, (len(self.symptom_dict), s))
                if not s in self.ds_rind:
                    self.ds_rind[s] = {} 
                self.ds_rind[s][id] = self.disease_rate[id]
            self.symptom_dict.make_automaton()
        print('init succeed ... type symptoms ...', file = sys.stderr)

    def extract_self_explain(self, req):
        fea_list = []
        #todo: 利用ac和同义词表，解析出更多表述的症状特征
        for word in self.symptom_dict.iter(req['request']['text']):
            sym = 'S_' + word[1][1]
            if sym in self.fea_map:
                fea_list.append((sym, 0))

        #todo: 抽取部位特征

        return fea_list

    def extract_interactive(self, req_list):
        fea_list = []
        #todo: 利用机器询问和用户回答，解析出新特征
        for req in req_list[:-1]:
            for word in req['request']['text'].split(' '):
                sym = 'S_' + word
                if sym in self.fea_map:
                    fea_list.append((sym, 0))
        return fea_list

    def get_observed_info(self, req_list):
        observed_info = {}
        for fea, val in self.extract_self_explain(req_list[-1]):
            observed_info[fea] = val
        for fea, val in self.extract_interactive(req_list):
            observed_info[fea] = val
    
        observed_info['SEX'] = req_list[-1]['user']['sex']
        observed_info['AGE'] = age_id(req_list[-1]['user']['age'])

        return observed_info 

    def fea_to_id(self, observed_info):
        ret = {}
        for fea, val in observed_info.items():
            key = fea
            if fea in self.fea_map:
                key = self.fea_map[fea]
            ret[key] = val
        return ret    

    def get_candidate_list(self, observed_info):
        candidates = {} 
        for fea, val in observed_info.items():
            if not fea.startswith('S_'):
                continue
            sym = fea[len('S_'):]
            if sym in self.disease_id:          #症状本身就是疾病名的情况
                kid = self.disease_id[sym]
                if not kid in candidates:
                    candidates[kid] = 0
                candidates[kid] += 1
            if sym in self.ds_rind:             
                for kid, rate in self.ds_rind[sym].items():
                    if not kid in candidates:
                        candidates[kid] = 0
                    candidates[kid] += rate    
        ids = sorted(candidates.items(), key=lambda d:d[1], reverse=True)[:20]
        print('%d candidates generated' % len(ids), file = sys.stderr)
        return ids

    def department_select(self, dep_list):
        if len(dep_list) == 0:
            return '', 0
        if len(dep_list) == 1:
            return dep_list[0]
        if dep_list[1][0].find(dep_list[0][0]) >= 0:
            return dep_list[1]
        return dep_list[0]

    def run(self, req_list):
        response = {'wei': 0, 'text': '', 'type': 0}

        if len(req_list) == 0:
            return response
        observed_info_ori = self.get_observed_info(req_list)
        print(observed_info_ori, file = sys.stderr)
        candidates = self.get_candidate_list(observed_info_ori)

        observed_info = self.fea_to_id(observed_info_ori)

        dw = {}
        deps = {}
        for i, r in candidates:
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
            return response
    
        for name, score in sorted(dw.items(), key=lambda d:d[1], reverse=True)[:10]:
            print('%s\t%.8f' % (name, score), file = sys.stderr)
    
        dep_list = sorted(deps.items(), key=lambda d:d[1], reverse=True)
        print('department: %s' % dep_list[:5], file = sys.stderr)

        response = {}
        dep, wei = self.department_select(dep_list)
        response['type'] = 0
        response['wei'] = 1000 * wei
        response['text'] = '建议就诊科室：' + dep
        return response

if __name__ == '__main__':
    d = Diagnosis()
    while 1:
        try:
            buf = input().rstrip()
        except:
            break
        req = {'user': {'sex': 1, 'age': 30}, 'request': {'text': buf, 'type': 0}}
        req_list = [req]
        for part in buf.split(' '):
            if part.startswith('age='):
                req['user']['age'] = int(part[len('age='):])
            if part.startswith('sex='):
                req['user']['sex'] = int(part[len('sex='):])
        response = d.run(req_list)
        print(req_list, file = sys.stderr)
        print(response, file = sys.stderr)
