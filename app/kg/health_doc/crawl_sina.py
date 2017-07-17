import sys
sys.path.append('../../../lib/dm/spider')
import urllib
from minisb import MiniSpider

retdir = '/data/health_doc/sina'
seeds = ['http://health.sina.com.cn', 
		'http://health.sina.com.cn/hc/2017-07-07/doc-ifyfuzny3458968.shtml',
		'http://health.sina.com.cn/d/2017-07-07/doc-ifyhwefp0200719.shtml']
white_list = [r'http://health\.sina\.com\.cn/.+?\.shtml']
sb = MiniSpider('%s/db' % retdir, '%s/page' % retdir, seeds, 
		white_list = white_list, thread_num = 3, time_sleep = 1,
		queue_max_size = 1e6, url_max_size = 1e9, file_max_size = 1e12)

if sb.prepare():
	sb.run()

