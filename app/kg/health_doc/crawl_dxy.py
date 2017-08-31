import sys
sys.path.append('../../../lib/dm/spider')
import urllib
from minisb_bloomfilter import MiniSpider

retdir = '/data/health_doc/dxy'
seeds = ['http://www.dxy.cn/res/medical/news_4', 
		'http://heart.dxy.cn/article/28584',
		'http://pediatr.dxy.cn/article/522750',
        'http://surg.dxy.cn/tag/appendicitis',
        'http://www.dxy.cn/']
white_list = [r'http://.+?\.dxy\.cn/\+?']
black_list = [r'http://i\.dxy\.cn/.+?',
              r'http://e\.dxy\.cn/.+?',
              r'http://drugs\.dxy\.cn/.+?',
              r'http://meeting\.dxy\.cn/.+?',
              r'http://.+?\.dxy\.cn/.+?/bbs/.+?',
              r'.+?\.png',
              r'http://d\.dxy\.cn/.+?']
download_list = [r'http://\w+.dxy.cn/article/\d+', r'http://\w+.dxy.cn/res/medical/*']
sb = MiniSpider('%s/db' % retdir, '%s/page' % retdir, seeds, black_list = black_list,
		white_list = white_list, download_list = download_list, thread_num = 1, time_sleep = 2,
		queue_max_size = 1e6, url_max_size = 1e9, file_max_size = 1e12)

if sb.prepare():
	sb.run()

