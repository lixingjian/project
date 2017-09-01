#coding = utf-8

import sys, os
import json, urllib, urllib.request
from jparser import PageModel


if __name__ == '__main__':
    if len(sys.argv) > 1:
        page_dir = sys.argv[1]
        for f in os.listdir(page_dir):
            html = open(page_dir + '/' + f).read()
            pm = PageModel(html)
            result = pm.extract()
            print(result)

    while 1:
        try:
            url = input().strip()
        except:
            break
        html = urllib.request.urlopen(url).read().decode('utf-8')
        pm = PageModel(html)
        result = pm.extract()
        print(url + '\t' + str(result))
