#!/usr/bin/python
#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import random
import json

class Chat:#class defination 

	def __init__(self,inputContent):
		self.inputContent = json.loads(inputContent)
		self.possibleOutput = ['Hello','您好','再见','None']#Array for possible output
		self.executionLevels = {'Hello':0.2,'您好':0.3,'再见':0.2,'None':0}#Dictionary to map execution level
		self.outputContent = self.possibleOutput[random.randint(0,len(self.possibleOutput)-1)]#random output
		self.furtherQuestion = False
		self.currentExecutionLevel = 0
		self.executionLevelLookUp(self.outputContent)
		self.isFurtherQuestion()
		

	def executionLevelLookUp(self, outputContent):#map execution level
		lv = self.executionLevels[outputContent]
		self.currentExecutionLevel = lv
		return lv

	def isFurtherQuestion(self):#tracking the continuity of current conversation
		exLv = self.executionLevelLookUp(self.outputContent)
		if(exLv < 0.25):
			self.furtherQuestion = True
			return True
		else:
			self.furtherQuestion = False
			return False
	def ifFurtherQuestion(self):
		if(self.isFurtherQuestion() == True):
			return('请问今天能帮到您什么?')
		else:
			return(None)





########################################################################

#c1 = Chat('see')
#print getattr(c1,'outputContent')
#print getattr(c1,'currentExecutionLevel')
#print getattr(c1,'furtherQuestion')
#print c1.executionLevels








