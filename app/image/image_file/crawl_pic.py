import sys
sys.path.append('../../../alg/basic')
sys.path.append('../../../lib/dm/spider')
import str_util
import urllib
from minisb import MiniSpider

retdir = '/data/image/img_src'
seeds = str_util.read_lines('./url.pic')
download_list = [r'http://.+?']
white_list = [r'x']
sb = MiniSpider('%s/db' % retdir, '%s/page' % retdir, seeds, 
		white_list = white_list, download_list = download_list, 
                thread_num = 1, time_sleep = 1,
		queue_max_size = 1e6, url_max_size = 1e9, file_max_size = 1e12)

if sb.prepare():
	sb.run()

