import sys
sys.path.append('../../../lib/dm/spider')
import urllib
from minisb_bloomfilter import MiniSpider

retdir = '/data/health_doc/aiaiyi'
seeds = ['http://www.iiyi.com', 
	 'http://www.iiyi.com/l-430-1.html',
	 'http://www.iiyi.com/l-443-1.html',
	 'http://www.iiyi.com/i/news',
	 'http://ks.iiyi.com', 
	 'http://bingli.iiyi.com']
white_list = [r'http://www\.iiyi\.com/\w+-\d+-\d+\.html',
		r'http://www\.iiyi\.com/i/dept/\d+\.html']
sb = MiniSpider('%s/db' % retdir, '%s/page' % retdir, seeds, 
		white_list = white_list, thread_num = 1, time_sleep = 0.1,
		queue_max_size = 1e6, url_max_size = 1e9, file_max_size = 1e12)

if sb.prepare():
	sb.run()

