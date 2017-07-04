#coding:utf-8
import sys, os, json
sys.path.append('../../../alg/basic')
import str_util

def get_dis(cont):
	r1 = str_util.cut_windows(cont, '<title>', '的症状')
	if len(r1) > 0:
		return r1[0]
	return ''

def get_sym(cont):
	r1 = str_util.cut_windows(cont, 'db f12 lh240 mb15', '</span>')
	if len(r1) != 1:
		return []
	r2 = str_util.cut_windows(r1[0], '\"_blank\">', '</a>')
	return r2

pagedir = sys.argv[1]
for page in os.listdir(pagedir):
	cont = open(pagedir + '/' + page).read()
	dis = get_dis(cont)
	sym_list = get_sym(cont)
	keyid = os.path.basename(page).split('.')[0]
	if dis != '' and len(sym_list) > 0:
		disease_info = {}
		disease_info['id'] = keyid
		disease_info['name'] = dis
		disease_info['symptoms'] = []
		for k in sym_list:
			disease_info['symptoms'].append({k:1})
		print(json.dumps(disease_info, ensure_ascii=False))	


