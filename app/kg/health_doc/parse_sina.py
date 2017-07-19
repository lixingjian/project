#coding = utf-8
import os, sys, json
from bs4 import BeautifulSoup

def parse(cont):
    ret = {}
    p1 = cont.find('url: ')
    p2 = cont.find('page: ')
    if p1 < 0 or p2 < 0:
        return ret
    ret['url'] = cont[p1 + len('url: '):p2].strip()
    html = cont[p2 + len('page: '):]
    #print(html)

    soup = BeautifulSoup(html, 'html.parser') 
    ret['title'] = soup.title.get_text().strip()
       
    tags = soup.find_all('div', class_ = 'content')
    if len(tags) == 1:
        text = ''
        for part in tags[0].find_all('p'):
            text += part.get_text().strip()
            text += '\n'
        ret['content'] = text
    return ret

    
pagedir = sys.argv[1] + '/'
for fid in os.listdir(pagedir):
    fp = open(pagedir + fid, 'rb')
    cont = fp.read().decode('utf-8', 'ignore')
    for part in cont.split('~EOF!'):
        try:
            ret = parse(part)
        except:
            continue    
        if 'content' in ret:
            print(json.dumps(ret, ensure_ascii = False))
    fp.close()        
