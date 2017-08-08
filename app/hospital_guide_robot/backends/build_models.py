#coding = utf8
from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
import os, sys, json
from pgmpy.readwrite import BIFReader, BIFWriter, XMLBIFReader, XMLBIFWriter, ProbModelXML, UAIReader, UAIWriter

def format_2d_prob(p0, arr1, arr2):
    ret = []
    for j in range(len(arr2)):
        for i in range(len(arr1)):
            ret.append(p0 * arr1[i] * arr2[j])
    return ret

def sub_vec(vec, num):
    ret = []
    for x in vec:
        ret.append(num - x)
    return ret    

def save_model(model, fpath):
    writer = BIFWriter(model)
    writer.write_bif(filename = fpath)

dinfos = {}
for line in open('disease_intro.json').readlines():
    j1 = json.loads(line.rstrip())['struct']
    dinfos[j1['name']] = j1

for line in open('disease_symptom.json').readlines():
    j2 = json.loads(line.rstrip())
    if j2['name'] in dinfos:
        dinfos[j2['name']]['symptoms'] = j2['symptoms']
for line in open('disease_organ.json').readlines():
    j3=json.loads(line.rstrip())
    if j3['name'] in dinfos:
        dinfos[j3['name']]['organs']=j3['organ']


os.system('mkdir -p models')
d_map = {}
s_map = {}
o_map = {}
for name, dinfo in dinfos.items():
    disease_name = 'D_' + name    

    if not disease_name in d_map:
        d_map[disease_name] = 'D%d' % len(d_map)
    disease_id = d_map[disease_name]    
    dep_nodes = []
    if not 'symptoms' in dinfo:
        continue
    for symptom, prob in dinfo['symptoms'].items():
        dep_nodes.append(('SEX', disease_id))
        dep_nodes.append(('AGE', disease_id))
        symptom_name = 'S_' + symptom
        if not symptom_name in s_map:
            s_map[symptom_name] = 'S%d' % len(s_map)
        symptom_id = s_map[symptom_name]    
        dep_nodes.append((disease_id, symptom_id))
    
    dis_sym_name = 'S_' + name
    if not dis_sym_name in s_map:
        s_map[dis_sym_name] = 'S%d' % (len(s_map))
    dis_sym_id = s_map[dis_sym_name]
    dep_nodes.append((disease_id, dis_sym_id))
        

    if not 'organs' in dinfo:
        continue
    for organ, prob in dinfo['organs'].items():
        organ_name = 'O_' + organ
        if not organ_name in o_map:
            o_map[organ_name] = 'O%d' % len(o_map)
        organ_id=o_map[organ_name]
        dep_nodes.append((disease_id,organ_id))

    model = BayesianModel(dep_nodes)
    
    sex_prob = [0.5, 0.5]
    age_prob = [0.1, 0.1, 0.2, 0.2, 0.2, 0.2]
    cpd = TabularCPD(variable = 'SEX', variable_card = 2, values = [sex_prob])    #female, male
    model.add_cpds(cpd)
    cpd = TabularCPD(variable = 'AGE', variable_card = 6, values = [age_prob]) #0-1, 1-10, 10-20, 20-40, 40-60, 60+
    model.add_cpds(cpd)

    cpd = TabularCPD(variable = s_map['S_' + name], variable_card = 2, values = [[1, 0], [0, 1]], evidence = [disease_id], evidence_card = [2])
    model.add_cpds(cpd)

    sex_prob = [dinfo['sex'][0][1], dinfo['sex'][1][1]]
    age_prob = []
    for ageinfo in dinfo['age']:
        age_prob.append(ageinfo[1])
    piror_prob = format_2d_prob(dinfo['rate'], sex_prob, age_prob)
    cpd = TabularCPD(variable = disease_id, variable_card = 2, values = [piror_prob, sub_vec(piror_prob, 1)], evidence = ['SEX', 'AGE'], evidence_card = [len(sex_prob), len(age_prob)]) 
    model.add_cpds(cpd)
    for symptom, prob in dinfo['symptoms'].items():
        cpd = TabularCPD(variable = s_map['S_' + symptom], variable_card = 2, values = [[prob,0.2], [1-prob,0.8]], evidence = [disease_id], evidence_card = [2])
        model.add_cpds(cpd)
    

    for organ,prob in dinfo['organs'].items():
        cpd = TabularCPD(variable = o_map['O_' + organ], variable_card = 2,values = [[prob,0.1],[1-prob,0.9]],evidence = [disease_id],evidence_card = [2])
        model.add_cpds(cpd)
    model.check_model()
    save_model(model, 'models/model.bif.%s' % dinfo['id'])
    print('%s model saved' % name)

fp_fea = open('models/feature.id', 'w')
for name, fid in d_map.items():
    fp_fea.write(name + '\t' + fid + '\n')
for name, fid in s_map.items():
    fp_fea.write(name + '\t' + fid + '\n')
for name, fid in o_map.items():
    fp_fea.write(name + '\t' + fid + '\n')
fp_fea.close()    
