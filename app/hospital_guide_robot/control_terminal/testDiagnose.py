#!/usr/bin/python
#coding=utf-8
import sys
import random
import json

class Diagnosis:#class defination 

	def __init__(self,inputContent):
		self.inputContent = json.loads(inputContent)
		self.possibleOutput = ['内科','外科','骨科','None']#Array for possible output
		self.executionLevels = {'内科':0.7,'外科':0.8,'骨科':0.7,'None':0}#Dictionary to map execution level
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
		if(exLv < 0.75):
			self.furtherQuestion = True
			return True
		else:
			self.furtherQuestion = False
			return False
	def ifFurtherQuestion(self):
		if(self.isFurtherQuestion() == True):
			return('请问您哪儿疼?')
		else:
			return(None)









