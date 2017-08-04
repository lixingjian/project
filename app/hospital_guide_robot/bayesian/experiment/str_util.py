#coding = utf-8

import sys

'''
@功能：截取text中tag1和tag2中间的内容
@返回值：list，表示每段tag1和tag2中间的内容
'''
def cut_windows(text, tag1, tag2):
	ret = []
	while True:	
		p1 = text.find(tag1)
		if p1 < 0:
			break
		begin = p1 + len(tag1)
		p2 = text[begin:].find(tag2)
		if p2 < 0:
			break
		end = begin + p2
		ret.append(text[begin:end])
		if end == len(text):
			break
		text = text[end + 1:]
	return ret	

'''
@功能：输入字符串s，得到s中的数字，输入必须是UTF-8编码
@返回值：list，每个元素表示一个数字单元，每个数字单元包含以下字段：
	begin: 数字在s中的起始位置
	end: 数字在s中的结束位置
	value：数值大小，float类型list，长度为1表示单个数值，长度为2表示区间
	unit：单位
'''
range_tags = set(['-', '--', '---', '~', '~~', '——', '到', '至'])
units = set(['%', '岁', '年', '天', '日'])
def num_extract(s):
	ori_list = []
	begin = -1
	s += '\n'
	for i in range(len(s)):
		c = s[i]
		if (ord(c) >= ord('0') and ord(c) <= ord('9')) or c == '.':
			if begin < 0 and c != '.':
				begin = i
		elif begin >= 0:
			end = i
			value = float(s[begin:i])
			unit = 'None'
			for u in units:
				if s[i:].startswith(u):
					unit = u
					end += len(u)
					break
			if unit == '%':
				value = 0.01 * value
			vals = [value]	
			if s[end:].startswith('以上'):
				vals = [value, value * 100]
			elif s[end:].startswith('以下'):
				vals = [value * 0.01, value]
			num = (begin, end, vals, unit)
			ori_list.append(num)
			begin = -1

	merge_list = []
	for i in range(len(ori_list)):
		cur_unit = ori_list[i]
		if i == 0:
			merge_list.append(cur_unit)
			continue
		last_unit = merge_list[len(merge_list) - 1]
		if s[last_unit[1]:cur_unit[0]].strip() in range_tags and len(last_unit[2]) == 1 and len(cur_unit[2]) == 1:	#如果上一个数字单元是单个数字，并且中间是区间符号
			last_val = last_unit[2][0]
			if last_unit[3] == 'None' and cur_unit[3] == '%':
				last_val = 0.01 * last_val
			merge_list[len(merge_list) - 1] = (last_unit[0], cur_unit[1], [last_val] + cur_unit[2], cur_unit[3])
		else:
			merge_list.append(cur_unit)
	return merge_list		

def read_kv_file(filename):
	ret = {}
	for line in open(filename).readlines():
		line = line.rstrip()
		p = line.find('\t')
		if p <= 0:
			print('warning: invalid line %s' % line, file = sys.stderr)
			continue
		key = line[:p]
		val = line[p+1:]
		if key in ret:
			print('warning: dumplicated key %s' % key, file = sys.stderr)
			continue
		ret[key] = val
	return ret	

if __name__ == '__main__':
	for line in open('/home/work/data/unit_test/test.num_extract').readlines():
		line = line.rstrip()
		print('%s\t%s' % (line, num_extract(line)))
