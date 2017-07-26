#!/usr/bin/python
#coding=utf-8
from testChat import Chat
from testDiagnose import Diagnosis
from testGuide import Guide
import sys
import json
import random
sys.path.append("/home/work/github/project/app/hospital_guide_robot/general_knowledge_search/")
from Search import Searching

#input content 
#json.loads(upstream)
selfExplaination = '糖sdd'
inputType = ['userEnter','userSelection','userVoiceEnter']
#Userinfo
name = ''
sex = ''
age = 0
race = ''
address = ''
allergicHistory = []
pMH = {'传染病' : 'None', '老年痴呆':'None', '体瘤':'None', '脑栓塞':'None', '眼屈光不正':'None', 
		'视网膜病变':'None', '中耳病变':'None', '鼻窦病变':'None', '甲状腺功能异常':'None', 
		'皮肤病':'None', '肺病':'None', '心脏病':'None', '呼吸道疾病':'None', '食道疾病':'None',
		'肠疾病':'None', '正中神经损伤':'None', '骨折骨裂':'None', 
		'关节病变':'None', '肌肉功能异常':'None', '肝炎（甲乙丙丁肝炎）':'None', '肝功能异常':'None', '胃病':'None', 
		'胰腺病':'None', '胆病':'None', '男性疾病':'None', '女性疾病':'None', '性传染疾病':'None', '直肠以及肛门疾病':'None',
		'肾病':'None', '全身代谢功能异常':'None', '血症':'None','儿科疾病':'None', '其他':'None'}
userInfo = {'姓名' : name, '性别' : sex, '年龄' : age, '名族' : race, '地址' : address, '过敏史' : allergicHistory, '既往病史': pMH}
#current status
bodyTemp = 0.0
bloodPressure = {'High' : 0, 'Low' : 0}
levelOfPain = 0
currentMedUse = []
curentStatus = {'体温':bodyTemp , '血压' : bloodPressure , '疼痛程度' : levelOfPain, '当前服用药物' : currentMedUse}
#synthesize 
questionDict = {}
inputContent = {'Self Explaination' : selfExplaination , 'Input Type' : inputType[0] , 
				'User Info' : userInfo, 'Current Status' : curentStatus, 'Interacting History' : questionDict}
#Sim further question
upstreamData = json.dumps(inputContent , ensure_ascii = False)






class Terminal:
    #initialize
    def __init__(self,upstreamData):
        self.furtherQuestions = []
        self.isFurtherQuestion = False
        self.inputContent = json.loads(upstreamData)
        self.dataPassDown()

    #Select the option with the highest execution level
    def selection(self):
        e1 = getattr(self.c1,'currentExecutionLevel')
        e2 = getattr(self.d1,'currentExecutionLevel')
        e3 = self.g1.getExecutiveLevel()
        n1 = getattr(self.c1,'outputContent')
        n2 = getattr(self.d1,'outputContent')
        n3 = getattr(self.g1,'result')
        eList = [e1,e2,e3]
        self.sort(eList)
        if(eList[0] == e1):
            self.selected = self.c1
            self.selectedNum = 1
            return n1
        elif(eList[0] == e2):
            self.selected = self.d1
            self.selectedNum = 2
            return n2
        else:
            self.selected = self.g1
            self.selectedNum = 3
            return n3

	#SORT numbers, from big to small
    def sort(self,l):
        for i in range(1, len(l)):
            j = i-1
            key = l[i]
            while (l[j] < key) and (j >= 0):
                l[j+1] = l[j]
                j -= 1
            l[j+1] = key

	#put questions and its answer into a dictionary
    def questionSynthesis(self,question):
        ans = self.getAnswerFromUpstream(self.furtherQuestion)
        self.inputContent['Interacting History'][self.furtherQuestion] = ans
        return

	#First time passing down data
    def dataPassDown(self):
        passDownContent = json.dumps(self.inputContent, ensure_ascii = False)
        self.c1 = Chat(passDownContent)
        self.d1 = Diagnosis(passDownContent)
        self.g1 = Searching()
        self.g1.run(passDownContent)


	#Pass down data from continous interaction
    def dataPassDownWithQuestions(self):
        passDownContent = json.dumps(self.inputContent, ensure_ascii = False)
        if(self.selectedNum == 1):
            self.c1 = Chat(passDownContent)
            self.isQues = self.c1.isFurtherQuestion()
        elif(self.selectedNum == 2):
            self.d1 = Diagnosis(passDownContent)
            self.isQues = self.d1.isFurtherQuestion()
        else:
            self.g1 = Guide()
            self.isQues = False #self.g1.isFurtherQuestion()
        return

	#pass up data to interacting pannel
    def dataPassUp(self):
        return(self.furtherQuestion)

    #SIMULATING GET ANSWER VOID
    def getAnswerFromUpstream(self,furtherQuestion):
        return('我头疼')

	#Run method
    def run(self):
        self.upstreamData = json.loads(upstreamData)
        self.dataPassDown()#First time pass down
        self.selection()#Select the option with the highest execution level
        #print self.selected.isFurtherQuestion()
        self.isQues = self.selected.isFurtherQuestion()
        while(self.isQues == True):#keep feeding 
            self.furtherQuestion = self.selected.ifFurtherQuestion()
            print(self.furtherQuestion)
            self.questionSynthesis(self.furtherQuestion)
            self.dataPassDownWithQuestions()
        print(self.selected.outputContent)
        print(self.inputContent['Interacting History'])
        #Add reset here in the future
        return 
t1 = Terminal(upstreamData)

t1.run()























