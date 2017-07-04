#coding:utf-8
import sys, os, json
sys.path.append('../../../alg/basic')
import str_util

def get_dis(cont):
	r1 = str_util.cut_windows(cont, '<title>', '的简介')
	if len(r1) > 0:
		return r1[0]
	return ''

def get_rate(cont):
	r1 = str_util.cut_windows(cont, '患病比例：</span><span class=\"fl txt-right\">', '</span></p>')
	if len(r1) > 0:
		return r1[0].strip()
	return ''

def parse_rate(ori):
	nlist = str_util.num_extract(ori)
	if len(nlist) == 0:
		sys.stderr.write('warning: number extracted failed:%s\n' % ori)
	
	ratelist = []
	for begin, end, vals, unit in nlist:
		if unit != '%' or len(vals) == 0:
			continue
		rate = float(sum(vals)) / len(vals)
		ratelist.append(rate)
	rate = 1e-8	
	if len(ratelist) == 0:
		if ori.find('常见病') >= 0:
			rate = 1e-3
	else:
		rate = ratelist[0]
	
	rate = round(rate, 8)
	return rate

def get_group(cont):
	r1 = str_util.cut_windows(cont, '易感人群：</span><span class=\"fl txt-right\">', '</span></p>')
	if len(r1) > 0:
		return r1[0].strip()
	return ''

def get_department(cont):
	r1 = str_util.cut_windows(cont, '就诊科室：</span><span class=\"fl txt-right\">', '</span></p>')
	if len(r1) > 0:
		return r1[0].strip()
	return ''

def parse_department(s):
	ret = []
	for ss in s.split(' '):
		ss = ss.strip()
		if len(ss) > 1:
			ret.append(ss)
	return ret		

age_info = [('0-1', 0, 1, ['婴幼儿', '婴儿', '新生儿', '小儿', '儿童', '儿科', '男孩', '女孩']), 
		    ('1-10', 1, 10, ['婴幼儿', '幼儿', '小儿', '少年', '青少年', '儿童', '儿科', '男孩', '女孩']), 
			('10-20', 10, 20, ['青年', '青少年', '男孩', '女孩']), 
			('20-40', 20, 40, ['成年', '青年', '中青年', '妊娠', '哺乳', '妇科', '男科', '产科', '妇产']),
			('40-60', 40, 60, ['成年', '中年', '中老年', '中青年', '妇科', '男科']),
			('60-', 60, 200, ['成年', '老年', '中老年', '老人'])
			]
sex_info = [('m', ['男']), ('f', ['女','妇'])]

def init_dict(intro):
	ret = {}
	for ii in intro:
		ret[ii[0]] = 1e-6
	return ret

def prob_norm(d):
	s = 1e-10
	for k, v in d.items():
		s += v
	for k in d.keys():
		d[k] = round(d[k] / s, 4)

def calc_age_prob(dori):
	ret = init_dict(age_info)
	for name, age_min, age_max, tag_list in age_info:
		for num_unit in str_util.num_extract(dori['rate'] + '。' + dori['group']):
			_, _, vals, unit = num_unit
			if unit != '岁' or len(vals) != 2:
				continue
			if vals[0] < age_max and vals[1] >= age_min and vals[0] < vals[1]:	
				ret[name] += 1
		for tag in tag_list:
			ret[name] += (dori['name'] + dori['group'] + dori['department']).count(tag)
	prob_norm(ret)		
	return ret

def calc_sex_prob(dori):
	ret = init_dict(sex_info)
	for name, tag_list in sex_info:
		 for tag in tag_list:
			 ret[name] += (dori['name'] + dori['group'] + dori['department']).count(tag)
	prob_norm(ret)
	return ret

pagedir = sys.argv[1]
for page in os.listdir(pagedir):
	cont = open(pagedir + '/' + page).read()
	dis = get_dis(cont)
	if dis == '':
		continue
	keyid = os.path.basename(page).split('.')[0]
	disease_info = {}
	disease_info['ori'] = {}
	dori = disease_info['ori']
	dori['name'] = dis
	dori['rate'] = get_rate(cont)
	dori['group'] = get_group(cont)
	dori['department'] = get_department(cont)

	disease_info['struct'] = {}
	dstu = disease_info['struct']
	dstu['id'] = keyid
	dstu['name'] = dis
	dstu['rate'] = parse_rate(dori['rate'])
	dstu['age'] = sorted(calc_age_prob(dori).items())
	dstu['sex'] = sorted(calc_sex_prob(dori).items())
	dstu['department'] = parse_department(dori['department'])
	print(json.dumps(disease_info, ensure_ascii=False))	

#end
