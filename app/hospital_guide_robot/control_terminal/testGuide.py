#!/usr/bin/python
#coding=utf-8
import sys
import random
import json

class Guide:#class defination 

	def __init__(self,inputContent):
		self.inputContent = json.loads(inputContent)
		self.possibleOutput = ['外科在您身后二十米','内科在二楼西侧','发烧通常是由炎症引起的','None']#Array for possible output
		self.executionLevels = {'外科在您身后二十米':0.4,'内科在二楼西侧':0.4,'发烧通常是由炎症引起的':0.3,'None':0}#Dictionary to map execution level
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
		if(exLv < 0.35):
			self.furtherQuestion = True
			return True
		else:
			self.furtherQuestion = False
			return False
	def ifFurtherQuestion(self):
		if(self.isFurtherQuestion() == True):
			return('请问您去哪儿?')
		else:
			return(None)










