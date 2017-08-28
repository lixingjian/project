#coding:utf-8   #强制使用utf-8编码格式
import os

f = open("../log/1502929386_crawerNumUrl.log",'r')

content = f.read()

f.close()


print(content)
emailStr1 = 'echo "邮件正文内容" | mail -s "邮件主题"  chen_lee@126.com'

emailStr = 'echo '+'"'+content+'"'+' | mail -s "邮件主题"  chen_lee@126.com'
#emailStr = 'mail -s "状态监控" chen_lee@126.com < ../log/1502929386_crawerNumUrl.log'


os.system(emailStr)

