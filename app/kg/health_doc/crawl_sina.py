from minisb import MiniSpider

seeds = ['http://health.sina.com.cn', 
		'http://health.sina.com.cn/hc/2017-07-06/doc-ifyhwefp0138273.shtml',
		'http://health.sina.com.cn/healthcare/',
		'http://health.sina.com.cn/hc/2017-07-03/doc-ifyhrxsk1594050.shtml']
white_list = [r'http://health.sina.com.cn/*']
sb = MiniSpider('./testdb', './testpage', seeds, 
		white_list = white_list, thread_num = 5, time_sleep = 0.1,
		queue_max_size = 1e6, url_max_size = 1e4, file_max_size = 1e9)

if sb.prepare():
	sb.run()

