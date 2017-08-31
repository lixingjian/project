import sys
sys.path.append('../../../lib/dm/spider')
import urllib
from minisb_bloomfilter import MiniSpider

retdir = '/data/health_doc/haodf'
seeds = ['http://www.haodf.com/keshi/list.htm', 
         'http://www.haodf.com/keshi/DE4r0PiRvNoMFwIj8vHRbuflCII2Ip/wenzhang.htm?p=5',
		 'http://www.haodf.com/zhuanjiaguandian/drqinwei_5138477001.htm']

download_list = [r'http://www\.haodf\.com/zhuanjiaguandian/[0-9a-z_]+\.htm']
white_list = download_list + [r'http://www\.haodf\.com/keshi/list\.htm', 
              r'http://www\.haodf\.com/keshi/[0-9a-zA-Z]+\.htm',
              r'http://www\.haodf\.com/keshi/\w+/wenzhang\..+?']
sb = MiniSpider('%s/db' % retdir, '%s/page' % retdir, seeds, 
		download_list = download_list, white_list = white_list, thread_num = 2, time_sleep = 0.1,
		queue_max_size = 1e6, url_max_size = 1e9, file_max_size = 1e12)

if sb.prepare():
	sb.run()

