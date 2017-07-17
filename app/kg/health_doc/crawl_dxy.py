import sys
sys.path.append('../../../lib/dm/spider')
import urllib
from minisb import MiniSpider

retdir = '/data/health_doc/dxy'
seeds = ['http://www.dxy.cn/res/medical/news_4', 
		'http://heart.dxy.cn/article/28584',
		'http://pediatr.dxy.cn/article/522750']
white_list = [r'http://\w+.dxy.cn/article/\d+', r'http://\w+.dxy.cn/res/medical/*']
sb = MiniSpider('%s/db' % retdir, '%s/page' % retdir, seeds, 
		white_list = white_list, thread_num = 1, time_sleep = 5,
		queue_max_size = 1e6, url_max_size = 1e9, file_max_size = 1e12)

if sb.prepare():
	sb.run()

