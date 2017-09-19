import sys
sys.path.append('../../../lib/dm/spider')
import urllib
from minisb_v1_0 import MiniSpider

retdir = '/data/health_doc/dxy'
proxy_dir = '/data/lichengDownload/my_proxy_pool/proxy_getter/'
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
              r'http://d\.dxy\.cn/.+?',
              r'http://pcicase\.dxy\.cn/.+?',
              r'http://club\.dxy\.cn/.+?`',
              r'http://sinefly\.dxy\.cn/.+?',
              r'http://hematology-lecture2010\.dxy\.cn/.+?',
              r'http://best\.dxy\.cn/.+?',
              r'http://tong\.dxy\.cn/.+?',
              r'http://infect\.dxy\.cn/.+?',
              r'http://auth\.dxy\.cn/.+?',
              r'http://contest\.dxy\.cn/.+?',
              r'http://jieyan\.dxy\.cn/.+?',
              r'http://search\.dxy\.cn/.+?',
              r'http://yyh\.dxy\.cn/.+?',
              r'http://dq\.dxy\.cn/.+?',
              r'http://lilly.dxy.cn/',
              r'http://learning.dxy.cn',
              r'http://vs.dxy.cn',
              r'http://g.dxy.cn',
              r'http://gg.dxy.cn',
              r'http://www.dxy.cn/bbs/.+?']

download_list = [r'http://\w+.dxy.cn/article/\d+', 
                 r'http://\w+.dxy.cn/res/medical/*',
                 r'http://\w+\.dxy\.cn/html/news/.+?']
sb = MiniSpider('%s/db' % retdir, '%s/page' % retdir, seeds, proxy_dir = proxy_dir,black_list = black_list,
		white_list = white_list, download_list = download_list, thread_num = 5, time_out = 10,time_sleep = 1,
		queue_max_size = 1e6, url_max_size = 1e9, file_max_size = 1e12)

if sb.prepare():
	sb.run()

