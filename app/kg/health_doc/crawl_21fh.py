import sys
sys.path.append('../../../lib/dm/spider')
import urllib
from minisb_bloomfilter import MiniSpider

retdir = '/data/health_doc/21fh'
seeds = ['http://zzk.fh21.com.cn', 
		 'http://dise.fh21.com.cn/articles/2743-6-3.html',
		 'http://dise.fh21.com.cn/department/illness/4-3.html'
         ]
download_list = [r'http://dise.fh21.com.cn/articles/.+?\.html',
              r'http://zzk.fh21.com.cn/symptom/detail/\d+\.html',  
              r'http://dise.fh21.com.cn/article/detail/\d+\.html',
              r'http://dise.fh21.com.cn/share/article/\d+\.html'
              ]
white_list = [r'http://.+?\.fh21\.com\.cn/.+?']

sb = MiniSpider('%s/db' % retdir, '%s/page' % retdir, seeds, 
		white_list = white_list, download_list = download_list, thread_num = 1, time_sleep = 0.1,
		queue_max_size = 1e6, url_max_size = 1e9, file_max_size = 1e12, debug = 0)

if sb.prepare():
	sb.run()

