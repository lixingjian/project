import sys
sys.path.append('../../../lib/dm/spider')
import urllib
from minisb_add_history_file import MiniSpider

retdir = '/data/health_doc/21fh'
seeds = ['http://zzk.fh21.com.cn', 
		 'http://dise.fh21.com.cn/articles/2743-6-3.html',
		 'http://dise.fh21.com.cn/department/illness/4-3.html'
         ]
download_list = [r'http://dise.fh21.com.cn/articles/.+?\.html',
              r'http://zzk.fh21.com.cn/symptom/detail/\d+\.html',  
              r'http://dise.fh21.com.cn/article/detail/\d+\.html',
              r'http://dise.fh21.com.cn/share/article/\d+\.html',
              r'http://dise.fh21.com.cn/articles/.+?',
              r'http://news.fh21.com.cn/hyzx/.+?',
              r'http://news.fh21.com.cn/qwfb/.+?',
              r'http://news.fh21.com.cn/lyt/ysbw/.+?',
              r'http://ssk.fh21.com.cn/sd.+?',
              r'http://hyk.fh21.com.cn/hyd.+?',
              r'http://test.fh21.com.cn/jkzc/show.+?',
              r'http://baby.fh21.com.cn/.*html',
              r'http://ys.fh21.com.cn/.*/\d.*html'
              ]
white_list = [r'http://.+?\.fh21\.com\.cn/.+?']

black_list = [r'.+?iask.fh21.com.cn/question/',
              r'http://yqk.fh21.com.cn/',
              r'http://news.fh21.com.cn/yyqy/.+?',
              r'http://news.fh21.com.cn/jksd/.+?',
              r'http://news.fh21.com.cn/ssbd/ysaq/.+?',
              r'http://yyk.fh21.com.cn/',
              r'http://sex.fh21.com.cn/',
              r'http://zjk.fh21.com.cn/',
              r'https://iask.fh21.com.cn/',
              r'http://myzx.fh21.com.cn/',
              r'http://ypk.fh21.com.cn/',
              r'http://www.fh21.com.cn/meirong/',
              r'http://exam.fh21.com.cn/',
              r'http://tcms.fh21.com.cn/',
              r'https://zx.fh21.com.cn/',
              r'http://news.fh21.com.cn/zt/',
              r'http://jianfei.fh21.com.cn/',
              r'http://beauty.fh21.com.cn/',
              r'http://lady.fh21.com.cn/',
              r'http://psy.fh21.com.cn/',
              r'http://care.fh21.com.cn/',
              r'http://news.fh21.com.cn/fangtan/zjft/'
              ]

sb = MiniSpider('%s/db' % retdir, '%s/page' % retdir, seeds, 
		white_list = white_list,black_list = black_list, download_list = download_list, thread_num = 5, time_sleep = 1,
		queue_max_size = 1e6, url_max_size = 1e9, file_max_size = 1e12, debug = 0)

if sb.prepare():
	sb.run()

