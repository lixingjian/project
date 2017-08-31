import sys
sys.path.append('../../../lib/dm/spider')
import urllib
from minisb_bloomfilter import MiniSpider

retdir = '/data/image/huaban/html'
seeds = ['http://huaban.com/pins/1233848533/'] 
download_list = [r'http://huaban.com/pins/\d+/']
white_list = [r'http://huaban.com/pins/\d+/', r'http://huaban.com/boards/\d+/']
sb = MiniSpider('%s/db' % retdir, '%s/page' % retdir, seeds, 
		white_list = white_list, download_list = download_list,
                thread_num = 1, time_sleep = 1, piror_mode = 1,
		queue_max_size = 1e6, url_max_size = 1e9, file_max_size = 1e12)

if sb.prepare():
	sb.run()

