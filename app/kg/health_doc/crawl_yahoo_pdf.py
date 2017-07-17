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

retdir = '/data/health_pdf/yahoo'
download_list = [r'http://.+?\.pdf', r'https://.+?\.pdf']
sb = MiniSpider('%s/db' % retdir, '%s/page' % retdir, seeds, time_out = 1, piror_mode = 0,
		white_list = download_list, download_list = download_list, thread_num = 10, time_sleep = 0.1,
		queue_max_size = 1e6, url_max_size = 1e9, file_max_size = 1e12)

if sb.prepare():
	sb.run()

