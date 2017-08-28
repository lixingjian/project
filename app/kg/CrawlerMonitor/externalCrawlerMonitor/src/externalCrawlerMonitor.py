#!usr/bin/env python
#coding=utf-8
import os
import codecs
import re

def FileNumUrl(Urllist,pathItem):	
	numUrl = 0
	for indexUrl in Urllist:
		
		path = pathItem + "/" + indexUrl
		print("start read " + path)
		file = open(path,'rb')
		#line = file.readline().decode(encoding='UTF-8',errors='ignore')
		line = file.readline()
		#lineB = line.decode(encoding='UTF-8')
		pageEncode = 'UTF-8'
		while line:
			# if "charset=" in line:
				# pageEncode = re.findall('charset=(.+)" />',line)
			#print(line)
			
			if b'~EOF!\n' == line:
				numUrl += 1
			#if '~EOF!' in  lineB:
				#print(lineB)
				#print(line)
			#line = file.readline().decode(encoding='UTF-8',errors='ignore')
			line = file.readline()
			#lineB = line.decode(encoding='UTF-8')
		file.close()
	return numUrl
		

def GetAllNumUrl(bigDir):
	#将日志存入文件
	fileLog = open("HealthDoc.log",'w')
	#获得当前文件下面的文件及文件夹列表
	pageList = os.listdir(bigDir)
	for indexDir in pageList:
	#pathHealthDoc可以替换
		pathItem = bigDir +"/" + indexDir
		if os.path.exists(pathItem) and os.path.isdir(pathItem):
			pathItem = pathItem + "/" + "page"
			#最终文件夹
			if os.path.exists(pathItem):
				#获得最终文件名
				pagePageList = os.listdir(pathItem)
				numUrl = FileNumUrl(pagePageList,pathItem)
				print("%s  %d" %(pathItem,numUrl))
				fileLog.write(str(pathItem) + "\t" + str(numUrl) + "\r\n")
				#print(pagePageList)
	fileLog.close()
	

	

#对应的相对地址，相对于当前目录
pathHealthDoc = "../../../../../../data/health_doc"
pathImage = "../../../../../../data/image"

GetAllNumUrl(pathHealthDoc)


