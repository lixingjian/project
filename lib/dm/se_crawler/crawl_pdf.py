#coding=utf-8
import sys
sys.path.append('../../../alg/basic')
import time, random
import urllib.request
import socket
import str_util
from urllib.error import URLError, HTTPError
socket.setdefaulttimeout(1)

def crawler(tag):
    url = ('https://search.yahoo.com/search?p=%s' % tag) + '+filetype%3apdf'
    #url = 'http://global.bing.com/search?q=糖尿病+filetype%3apdf&setmkt=en-us&setlang=en-us'
    url_req = urllib.parse.quote(url, safe=':/?=%+')  
    print(url_req)
    headers = {'User-Agent': r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
            r'Chrome/45.0.2454.85 Safari/537.36 115Browser/6.0.3',
            'Referer': r'http://www.lagou.com/zhaopin/Python/?labelWords=label',
            'Connection': 'keep-alive'
    }
    req = urllib.request.Request(url_req, headers=headers)
    try:
        page = urllib.request.urlopen(req).read().decode('utf-8').lower()
    except Exception as e:
        print('Error Http %s, url=%s' % (e, url_req), file = sys.stderr)
    #except URLError as e:
    #    print('Error Url %s, url=%s' % (e.reason, url_req), file = sys.stderr)
    else:
        print('Success, url=%s' % url_req, file = sys.stderr)
        return page
    return ''

def parse_res_list(cont):
    ret = []
    if cont == '':
        return set([])
    for url in str_util.cut_windows(cont, 'http%3a%2f%2f', '.pdf'):
        if url.find('<') >= 0 or url.find('>') >= 0:
            continue
        ret.append('http://%s.pdf' % url)
    for url in str_util.cut_windows(cont, 'https%3a%2f%2f', '.pdf'):
        if url.find('<') >= 0 or url.find('>') >= 0:
            continue
        ret.append('https://%s.pdf' % url)
    return set(ret)

i = 0
while 1:
    try:
        buf = input().rstrip()
    except:
        break
    page = crawler(buf)
    fp = open('tmp/%d_%s.html' % (i, buf), 'w')
    fp.write(page)
    fp.close()
    i += 1
    for url in parse_res_list(page):
        print(urllib.parse.unquote(url))
    time.sleep(random.randint(0,5))
