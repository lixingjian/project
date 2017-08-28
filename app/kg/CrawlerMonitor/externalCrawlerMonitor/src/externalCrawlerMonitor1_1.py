#!usr/bin/env python
#coding=utf-8
import os
import sys
import time


def FileNumUrl(Urllist,pathItem):	
	numUrl = 0
	for indexUrl in Urllist:		
		path = pathItem + "/" + indexUrl
		print("start read " + path)
		file = open(path,'rb')
		line = file.readline()
		while line:
			if b'~EOF!\n' == line:
				numUrl += 1
			line = file.readline()
		file.close()
	return numUrl
		

def GetAllNumUrlNew(pagesDir,logfile):
	pathItem = pagesDir
	#最终文件夹
	if os.path.exists(pathItem):
		#获得最终文件名
		pagePageList = os.listdir(pathItem)
		numUrl = FileNumUrl(pagePageList,pathItem)
		print("%s  %d" %(pathItem,numUrl))
		logfile.write(str(pathItem) + "\t" + str(numUrl) + "\r\n")


def search(path, word,logFile):
	for filename in os.listdir(path):
		fp = os.path.join(path, filename)
		if os.path.isdir(fp) and word in filename:
			if fp.find('img_src') == -1:
				print(fp)
				GetAllNumUrlNew(fp,logFile)
		elif os.path.isdir(fp):
			search(fp, word,logFile)

if __name__ == '__main__':

	
	#对应的相对地址，相对于当前目录
	pathHealthDoc = "../../../../../../data/health_doc"
	pathImage = "../../../../../../data/image"
	ticks = int(time.time())
	logPath = "../log/" + str(ticks) +"_crawerNumUrl.log"
	
	#logFile用于存储日志文件
	logFile = open(logPath,'w')
	search(pathHealthDoc,'page',logFile)
	search(pathImage,'page',logFile)
	logFile.close()
	


