import sys
sys.path.append('../../../lib/dm/spider')
import urllib
from minisb import MiniSpider

seeds = ['http://www.dxy.cn/res/medical/news_4', 
		'http://heart.dxy.cn/article/28584',
		'http://pediatr.dxy.cn/article/522750']
white_list = [r'http://\w+.dxy.cn/article/\d+', r'http://\w+.dxy.cn/res/medical/*']
sb = MiniSpider('./result/db.dxy', './result/page.dxy', seeds, 
		white_list = white_list, thread_num = 3, time_sleep = 1,
		queue_max_size = 1e6, url_max_size = 1e7, file_max_size = 1e11)

if sb.prepare():
	sb.run()

