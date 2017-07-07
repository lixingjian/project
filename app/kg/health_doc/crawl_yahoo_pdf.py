#coding=utf-8
import sys
sys.path.append('../../../lib/dm/spider')
import urllib
from minisb import MiniSpider

seeds = []
tag_list = open(sys.argv[1]).readlines()
for tag in tag_list:
	url = 'https://search.yahoo.com/search?p=%s' % tag
	url += '+filetype%3apdf'
	url_req = urllib.parse.quote(url, safe=':/?=%+') 
	seeds.append(url_req)

download_list = [r'http://.+?\.pdf', r'https://.+?\.pdf']
sb = MiniSpider('./result/db.pdf', './result/page.pdf', seeds, time_out = 1, piror_mode = 1,
		download_list = download_list, thread_num = 1, time_sleep = 0.1,
		queue_max_size = 1e6, url_max_size = 1e2, file_max_size = 1e11)

if sb.prepare():
	sb.run()

