import sys
sys.path.append('../../../lib/dm/spider')
import urllib
from minisb import MiniSpider

retdir = '/data/image/699pic/html'
seeds = ['http://699pic.com/'] 
download_list = [r'http://699pic.com/tupian-\d+\.html']
white_list = [r'http://699pic.com/tupian-\d+\.html', r'http://699pic.com/\w+\.html']
sb = MiniSpider('%s/db' % retdir, '%s/page' % retdir, seeds, 
		white_list = white_list, download_list = download_list, 
                thread_num = 1, time_sleep = 1,
		queue_max_size = 1e6, url_max_size = 1e9, file_max_size = 1e12)

if sb.prepare():
	sb.run()

