#!/bin/sh  
#Section configuration(配置部分)  
#Task Time ,example:203000(Time 20:30:00);190000(Time 19:00:00);  

startTimeMorning=060000 

startTimeEvening=180000   

 
#Section promgram (程序执行部分)  
  
echo ' program: Waiting...'  

while true ; do  
    curTime=$(date "+%H%M%S")  
    echo $curTime  
    if [ "$curTime" -eq "$startTimeMorning" ];then
        python externalCrawlerMonitor.py
		#python test.py
    fi
	if [ "$curTime" -eq "$startTimeEvening" ];then
        python externalCrawlerMonitor.py
		#python test.py
    fi
	
    sleep 1 
done  
