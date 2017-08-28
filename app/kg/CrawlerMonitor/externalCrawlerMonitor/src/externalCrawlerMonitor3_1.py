#!usr/bin/env python
#coding=utf-8
import os
import sys
import time
import datetime

logPath = []
logFile = []
lastLogFile = []

def FileNumUrl(Urllist,pathItem):	
	numUrl = 0
	for indexUrl in Urllist:		
		path = pathItem + "/" + indexUrl
		#print("start read " + path)
		file = open(path,'rb')
		line = file.readline()
		while line:
			if b'~EOF!\n' == line:
				numUrl += 1
			line = file.readline()
		file.close()
	return numUrl
		

def GetAllNumUrlNew(pagesDir):
	pathItem = pagesDir
	#最终文件夹
	if os.path.exists(pathItem):
		
		#获得最终文件名
		pagePageList = os.listdir(pathItem)
		numUrl = FileNumUrl(pagePageList,pathItem)
		
		#上一次的状态
		try:
			lastLine = lastLogFile.readline()
			lineSplit = lastLine.split()
			lastNumUrl = int(lineSplit[1])
			print("%s  %d  %d %d" %(pathItem,numUrl,lastNumUrl,numUrl - lastNumUrl))
			logFile.write(str(pathItem) + "\t" + str(numUrl) + "\t" + str(numUrl - lastNumUrl) + "\r\n")
			
		except:
			lastNumUrlSta = 'Null'
			print("%s  %d  %s" %(pathItem,numUrl,lastNumUrlSta))
			logFile.write(str(pathItem) + "\t" + str(numUrl) + "\t" + "Null" + "\r\n")



def search(path, word):
	for filename in os.listdir(path):
		fp = os.path.join(path, filename)
		if os.path.isdir(fp) and word in filename:
			if fp.find('img_src') == -1:
				print(fp)
				GetAllNumUrlNew(fp)
		elif os.path.isdir(fp):
			search(fp, word)
			
def mailSend(mailAddress,filePath):
	#mailFile = open(filePath,'r')
	emailShell = 'mail -s "状态监控" '+mailAddress+' < '+filePath
	os.system(emailShell)
	
def mailSendNew(mailAddress,filePath):
	mailFile = open(filePath,'r')
	content = mailFile.read()
	mailFile.close()
	emailShell = 'echo '+'"'+content+'"'+' | mail -s "爬虫状态监控"  '+mailAddress
	os.system(emailShell)

if __name__ == '__main__':
	#对应的相对地址，相对于当前目录
	pathHealthDoc = "../../../../../../data/health_doc"
	pathImage = "../../../../../../data/image"
	
	#打开上一次的log日志，和本次做对比
	logList = os.listdir("../log/")
	logList.sort()
	lastLogPath = "../log/"+logList[len(logList) - 1]
	#lastLogPath = "../log/" + "1502929386_crawerNumUrl.log"
	#获得文件的创建时间
	lastLogTimeStamp = os.path.getmtime(lastLogPath)
	lastLogDate = datetime.datetime.fromtimestamp(lastLogTimeStamp)  
	print(lastLogDate)  
	print(lastLogPath)
	lastLogFile = open(lastLogPath,'r')
	#过滤掉文件头
	lastLine = lastLogFile.readline()
	lastLine = lastLogFile.readline()
	#mailSend('chen_lee@126.com',lastLogPath
	#mailSendNew('chen_lee@126.com',lastLogPath)
	
	#logFile用于存储当前的日志文件
	ticks = int(time.time())
	logPath = "../log/" + str(ticks) +"_crawerNumUrl.log"
	Date = datetime.datetime.fromtimestamp(time.time())  
	print(Date)
	logFile = open(logPath,'w')
	#加上文件头
	logFile.write("上一次日志文件创建时间: "+ str(lastLogDate) + "\r\n")
	logFile.write("本次日志文件创建时间: "+ str(Date) + "\r\n")
	search(pathHealthDoc,'page')
	search(pathImage,'page')
	logFile.close()
	
	#邮件发送
	mailSendNew('lixingjian@boe.com.cn',logPath)
	time.sleep(20)
	mailSendNew('chen_lee@126.com',logPath)
	#mailSend('chen_lee@126.com',logPath)
