#coding = utf-8

import sys

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
