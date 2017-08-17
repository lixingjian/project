#coding = utf8
import sys
sys.path.append('/home/work/xiexueci/project/alg/basic')
import str_util
from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
import json
from pgmpy.readwrite import BIFReader, BIFWriter, XMLBIFReader, XMLBIFWriter, ProbModelXML, UAIReader, UAIWriter
import ahocorasick
from Match import Match
import math
sys.path.append('linear_model')
import predict_linear


UNWANTED = ['内科','外科','普通内科','中医科','普内','普内科','儿科','五官科','普通外科','普外科','普外','急诊科']

def age_id(n):
    age_parts = [1, 10, 20, 40, 60]
    for i in range(len(age_parts)):
        if n < age_parts[i]:
            return i
    return len(age_parts)

class Diagnosis:
    def __init__(self):
        self.disease_part = {}     # Key is id, value is department
        self.disease_rate = {}     # key is id, value is rate
        for line in open('disease_intro.json').readlines():
            js = json.loads(line.rstrip())['struct'] 
            self.disease_rate[js['id']] = js['rate']
            self.disease_part[js['id']] = js['department']

        # fea_map is a dict; key is 'D_' + diseaeName or 'S_' + symptom
        # or 'O_' + organ and value is its index
        self.fea_map = str_util.read_kv_file('models/feature.id')
        self.disease_id = {}       # Key is disease name, value is id
        self.disease_name = {}     # Key is id, value is disease name
        self.ds_rind = {}          # Key is symptom, value is a dict whose key is id, value is rate
        self.ds_organ = {}         # Key is organ, value is a dict whose key is id, value is rate

        # Imported from Match.py to extract keywords from patient's description
        self.matcher = Match()
        self.matcher.load("disease_symptom.json", "disease_organ.json", "common.txt", "feeling.txt")
        
        # Construct disease_name, disease_id and ds_rind
        for line in open('disease_symptom_modified.json').readlines():
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
        
        # Construct ds_organ
        for line in open('disease_organ.json').readlines():
            js = json.loads(line.rstrip())
            id = js['id']
            if not id in self.disease_rate:
                continue
            for o, w in js['organ'].items():
                if not o in self.ds_organ:
                    self.ds_organ[o]={}
                self.ds_organ[o][id] = self.disease_rate[id] 
        

    def extract_self_explain(self, req):
        fea_list = []
        # 利用ac和同义词表，解析出更多表述的症状特征
        text = req['request']['text']
        text.replace(' ', '，')
        for eachPart in text.split('，'):
            if len(eachPart) == 0:
                continue
            temp = self.matcher.match(req['request']['text'], 'syn1.txt', 'disease_symptom.json').rstrip()
            description = self.matcher.combine(temp, 'organ.txt', 'feeling.txt')

        for word in description.split(' '):
            if len(word) == 0:
                continue
            if word in self.ds_rind or word in self.disease_id:  # word is a symptom or the disease itself
                word = 'S_' + word
            elif ('#' + word) in self.ds_rind:
                word = 'S_#' + word
            elif word in self.ds_organ: # word is an organ
                word = 'O_' + word
            else:
                continue

            if word in self.fea_map:
                fea_list.append((word, 0))

        # Example of a returned fea_list
        # [(S_腹泻, 0), (O_腹, 0)]
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


    """
    req_list is shown below
    req = {'user': {'sex': 1, 'age': 30}, 'request': {'text': buf, 'type': 0}}
    req_list = [req]
    """

    def get_observed_info(self, req_list):
        observed_info = {}   # Key is the same format as the key in fea_map, eg. S_腹泻
                             # Value is 0
        for fea, val in self.extract_self_explain(req_list[-1]):
            observed_info[fea] = val
        for fea, val in self.extract_interactive(req_list):
            observed_info[fea] = val
        
        # Other two keys in observed_info 
        observed_info['SEX'] = req_list[-1]['user']['sex']
        observed_info['AGE'] = age_id(req_list[-1]['user']['age'])

        return observed_info 

    def fea_to_id(self, observed_info):
        ret = {}
        for fea, val in observed_info.items():
            # Key gets the same key in observed_info first
            key = fea
            if fea in self.fea_map:
                # Change key to its index as specified in the file models/feature.id
                key = self.fea_map[fea]
            ret[key] = val

        return ret

    def get_candidate_list(self, observed_info):
        candidates = {} 

        # Construct candidates dict; key is id, value is rate
        for fea, val in observed_info.items():
            if fea.startswith('S_'):
                sym = fea[len('S_'):]
                if sym in self.ds_rind:
                    for kid, rate in self.ds_rind[sym].items():
                        if not kid in candidates:
                            candidates[kid] = 0
                        candidates[kid] += rate
                elif sym in self.disease_id:
                    kid = self.disease_id.get(sym)
                    if not kid in candidates:
                        candidates[kid] = 0
                    candidates[kid] += 1
            
            elif fea.startswith('O_'):
                organ = fea[len('O_'):]
                if organ in self.ds_organ:
                    for kid, rate in self.ds_organ[organ].items():
                        if not kid in candidates:
                            candidates[kid] = 0
                        candidates[kid] += rate
            
            else:
                continue
            
        # Get the top 20 possible diseases
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
        if dep_list[0][0] in UNWANTED:
            if dep_list[1][0] in UNWANTED:
                if dep_list[2][0]==None:
                    return dep_list[1]
                return dep_list[2]
            return dep_list[1]
        return dep_list[0]

    def create_common_dict(self, commonSymFile):
        common_dict = {}     # Key is a list of symptoms, value is dept
        for line in open(commonSymFile).readlines():
            content = line.split(' ')
            common_dict[content[0]] = content[1].rstrip()
        return common_dict
            

    def find_obvious_sym (self, req_list, commonSymFile):
        common_dict = self.create_common_dict(commonSymFile)
        description = self.matcher.match(req_list[-1]['request']['text'], 'syn1.txt', 'disease_symptom.json').rstrip()
        for sym, dept in common_dict.items():
            found = True
            for ele in sym.split(','):
                if description.find(ele) < 0:
                    found = False
                    break
            if found == False:
                continue
            else:
                return dept
        return ''

    def run(self, req_list):
        response = {'wei': 0, 'text': '', 'type': 0}

        if len(req_list) == 0:
            return response
        observed_info_ori = self.get_observed_info(req_list)
        print(observed_info_ori, file = sys.stderr)

        response = {}
        response['type'] = 0
        response['wei'] = 1   # This may need modification


        # 模型第一层 - 简单症状的直接映射
        first_prediction = self.find_obvious_sym(req_list, 'common.txt')
        if len(first_prediction) != 0:
            # Prediction success
            response['text'] = first_prediction
            return response

        # 模型第二层 - 线性分类
        self.predict_linear = predict_linear.Diagnosis()
        Linear_prediction = self.predict_linear.run(req_list[-1]['request']['text'])
        response = Linear_prediction
        if response['text'] != '':
            return response
        else:
            pass
             



        # 模型第三层 - 贝叶斯网络的应用
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
            if math.isnan(score):
                score = 1
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

        dep, wei = self.department_select(dep_list)
        response['wei'] = 1000 * wei
        response['text'] = dep

        returnedCan = {}
        for did, rate in candidates:
            key = self.disease_name.get(did)
            returnedCan[key] = rate
        orderedCan = sorted(returnedCan.items(), key=lambda d:d[1], reverse = True)
        response['candidates'] = orderedCan
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
