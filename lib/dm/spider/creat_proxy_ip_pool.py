import urllib
import urllib.request
import time
import random
from lxml import etree

def get_url(url):     # 国内高匿代理的链接
    url_list = []
    for i in range(1,100):
        url_new = url + str(i)
        url_list.append(url_new)
    return url_list
    
def get_content(url):     # 获取网页内容
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 Safari/537.36 SE 2.X MetaSr 1.0'
    headers = {'User-Agent': r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                    r'Chrome/45.0.2454.85 Safari/537.36 115Browser/6.0.3',
                                    'Referer': r'http://www.lagou.com/zhaopin/Python/?labelWords=label',
                                                'Connection': 'keep-alive'
                                                                }
    headers['User-Agent'] = random.choice(user_agent)
#headers = {'User-Agent': user_agent}
    f = open('ip_pool','r')
    line = f.readlines()
    f.close()
    ip = line[5].split(u":")[0]
    port = line[5].split(u":")[1].strip('\n')
    proxy = {'http':'http://%s:%s'%(ip,port)}
    print(proxy)
#proxy_handler = urllib.request.ProxyHandler(proxy)
# opener = urllib.request.build_opener(proxy_handler)
#urllib.request.install_opener(opener)
    print(1)
    try:
        req = urllib.request.Request(url=url, headers=headers)
    except Exception as e:
        print('warning: Error request %s, url=%s' % (e, url))
    print(2)    
    retry = 0
    while retry < 10:
        try:
            res = urllib.request.urlopen(req)
            content = res.read()   
            print('read ok')
            return content.decode('utf-8')
        except Exception as e:
            print('warning: Error Http %s, url=%s' % (e, url))
            time.sleep(random.randint(1,3)) #等待1-3s
            retry += 1

def get_info(content):      # 提取网页信息 / ip 端口
    datas_ip = etree.HTML(content).xpath('//table[contains(@id,"ip_list")]/tr/td[2]/text()')
    datas_port = etree.HTML(content).xpath('//table[contains(@id,"ip_list")]/tr/td[3]/text()')
    with open("data.txt", "w") as fd:
        for i in range(0,len(datas_ip)):
            out = u""
            out += u"" + datas_ip[i]
            out += u":" + datas_port[i]
            fd.write(out + u"\n")     # 所有ip和端口号写入data文件
            

def verif_ip(ip,port):    # 验证ip有效性
    user_agent ='Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.22 Safari/537.36 SE 2.X MetaSr 1.0'
    headers = {'User-Agent':user_agent}
    proxy = {'http':'http://%s:%s'%(ip,port)}
    print(proxy)

    proxy_handler = urllib.request.ProxyHandler(proxy)
    opener = urllib.request.build_opener(proxy_handler)
    urllib.request.install_opener(opener)

    test_url = "https://www.baidu.com/"
    req = urllib.request.Request(url=test_url,headers=headers)
    time.sleep(6)
    try:
        res = urllib.request.urlopen(req)
        time.sleep(3)
        content = res.read()
        if content:
            print('that is ok')
            with open("data2.txt", "a") as fd:       # 有效ip保存到data2文件夹
                fd.write(ip + u":" + port)
                fd.write("\n")
        else:
            print('its not ok')
    except urllib.request.URLError as e:
        print(e.reason)
        
if __name__ == '__main__':
# url = 'http://www.xicidaili.com/nn/'
    url = 'http://www.kuaidaili.com/free/inha/'
    url_list = get_url(url)
    for i in url_list:
        print(i)
        content = get_content(i)
        time.sleep(3)
        get_info(content)
        

    with open("data.txt", "r") as fd:
        datas = fd.readlines()
        for data in datas:
            print(data.split(u":")[0])
            verif_ip(data.split(u":")[0],data.split(u":")[1])
