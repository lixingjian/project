#!usr/bin/env python
#coding=utf-8
import os
import sys
import time
import datetime

class Crawl_Monitor:
    def __init__(self,dir_list):
        self.dir_list = dir_list
    
    def dir_url_num(self,dir_path):
        url_num = 0
        for ele in os.listdir(dir_path):
            print(ele)
            f_path = os.path.join(dir_path, ele)
            f = open(f_path,'rb')
            for line in f:
                if b'~EOF!\n' == line:
                    url_num += 1
        return url_num

    def last_time_url_num(self):
        last_url_num_dict = {}
        log_name_list = os.listdir("../log/")
        if len( log_name_list) == 0:
            return last_url_num_dict
        log_name_list.sort()
        log_path = "../log/"+log_name_list[len(log_name_list) - 1]
        f = open(log_path, 'r')
        for line in f:
            line_list = line.split()
            last_url_num_dict[line_list[0]] = int(line_list[1])
        return last_url_num_dict

    def run(self):
        url_num_dict = {} 
        for ele in self.dir_list:
            url_num_dict[ele] = self.dir_url_num(ele)
        last_url_num_dict = self.last_time_url_num()
        ticks = time.time()
        self.new_f_name = '../log/' + str(ticks) + '_num_url.log'
        f = open(self.new_f_name, 'w')
        for key, val in url_num_dict.items():
            if key in last_url_num_dict.keys():
                res = key + ' ' + str(val) + ' ' + str(val - last_url_num_dict[key]) + '\n'
                f.write(res)
                print(res)
            else:
                res = key + ' ' + str(val) + ' ' + 'null' + '\n'
                f.write(res)
                print(res)
    
    def mail_send(self,mailAddress):
        mailFile = open(self.new_f_name,'r')
        content = mailFile.read()
        mailFile.close()
        emailShell = 'echo '+'"'+content+'"'+' | mail -s "爬虫状态监控"  '+mailAddress
        os.system(emailShell)

if __name__ == '__main__':
    dir_list = ['/data/qa_page/iask/page']
    cm = Crawl_Monitor(dir_list)
    cm.run()
    cm.mail_send('chen_lee@126.com')
