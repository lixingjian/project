import sys, os, time, random
import socket
import re
import leveldb
import threading
import urllib
import urllib.request
import urllib.parse
import requests
import traceback
from collections import deque
from bs4 import BeautifulSoup
sys.path.append('../../../alg/basic')
import str_util
import proxyip

user_agents = [  
		       'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',  
			   'Opera/9.25 (Windows NT 5.1; U; en)',  
			   'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',  
			   'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',  
			   'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',  
			   'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',  
			   "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",  
               ] 

def get_site(url):
	try:
		r = urllib.parse.urlparse(url)
		return r.netloc
	except:
		return ''

def check_key(db_name, key):
	while 1:	#其他进程可能在用db，所以要while try
	#try:
		if 1:	
			db = leveldb.LevelDB(db_name)
			break
		else:
		#except:
			print('fatal: db init failed', file = sys.stderr)
			time.sleep(random.randint(0, 10) * 0.01)
			continue
		
	val = ''
	try:
		val = db.Get(bytes(key, encoding = 'utf-8'))
		return True
	except:
		return False

def add_kv(db_name, key, val):
	while 1:
		if 1:
			db = leveldb.LevelDB(db_name)
			break
		else:
		#except:
			print('fatal: db init failed', file = sys.stderr)
			time.sleep(random.randint(0, 10) * 0.01)
			continue
	while 1:
		try:
			db.Put(key, val)
			break	
		except:
			print('fatal: db put failed', file = sys.stderr)
			continue


lock = threading.RLock()
class MiniSpider:
	def __init__(self, url_db_dir, result_dir, entry_list, white_list = [], black_list = [], download_list = [], piror_mode = 0, 
				thread_num = 1, time_out = 1, time_sleep = 1, queue_max_size = 1e6, url_max_size = 1e7, file_max_size = 1e10):

		self.url_db_dir = url_db_dir
		self.result_dir = result_dir
		self.entry_list = entry_list
		self.white_list = white_list
		self.black_list = black_list
		self.download_list = download_list
		self.piror_mode = piror_mode #0表示广度优先，1表示深度优先
		if len(self.download_list) == 0:
			self.download_list = self.white_list
		self.thread_num = thread_num
		self.time_out = time_out
		self.time_sleep = time_sleep
		self.queue_max_size = queue_max_size
		self.url_max_size = url_max_size
		self.file_max_size = file_max_size

	def prepare(self):
		self.url_num = 0
		self.file_id = 1
		self.file_len_cur = 0
		self.file_len_total = 0
		socket.setdefaulttimeout(self.time_out)
		self.url_queue = [] 
		for url in self.entry_list:
			self.url_queue.append(url)
		os.system('mkdir -p %s' % self.result_dir)
		#todo: 判断目录是否存在
		#todo: 判断其他数值参数是否合理
		return True

	#每个线程工作过程：pop一个url，判断是否已经在db中，如果在则继续pop，直到得到或队列空；抓取，如果成功则存储并且解析超链接加入队列，否则下一次pop
	def pop_url(self):
		lock.acquire()
		new_url = ''
		if self.url_queue:
			if self.piror_mode == 0:
				new_url = self.url_queue.pop(0)
			else:
				new_url = self.url_queue.pop()
		lock.release()
		return new_url

	def check_link(self, url):
		if not (url.startswith('http://') or url.startswith('https://')):
			return False
		for pattern in self.black_list:
			if re.match(pattern, url) != None:
				return False
		if len(self.white_list) == 0:
			return True
		valid = False
		for pattern in self.white_list:
			#print('%s\t%s' % (pattern, url))
			if re.match(pattern, url) != None:
				valid = True
				break
		#print('valid=%d' % valid)	
		return valid	

	def check_save(self, url):
		valid = False
		for pattern in self.download_list:
			#print('%s\t%s' % (pattern, url))
			if re.match(pattern, url) != None:
				valid = True
				break
		if not valid:
			return False

		lock.acquire()
		url_visited = check_key(self.url_db_dir, url)
		lock.release()
		if url_visited:
			return False

		key = bytes(url, encoding = 'utf-8')
		val = bytes('%s\t%d\t%d' % (self.url_db_dir, self.file_id, self.file_len_cur), encoding = 'utf-8')
		lock.acquire()
		add_kv(self.url_db_dir, key, val)
		lock.release()
		return True	

	def crawl_url(self, url):
		headers = {'User-Agent': r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
            r'Chrome/45.0.2454.85 Safari/537.36 115Browser/6.0.3',
            'Referer': r'http://www.lagou.com/zhaopin/Python/?labelWords=label',
            'Connection': 'keep-alive'
			}
		headers['User-Agent'] = random.choice(user_agents)
		headers['referer'] = '%d.%d.%d.%d' % (random.randint(10,100), random.randint(10,100), random.randint(10,100), random.randint(10,100))
		page = b''
		try:
			req = urllib.request.Request(url, headers = headers)
		except Exception as e:
			print('warning: Error request %s, url=%s' % (e, url), file = sys.stderr)
		
		retry = 0
		while retry < 10:
			try:
				page = urllib.request.urlopen(url).read()	#type(page) = bytes
				break
			except Exception as e:
				print('warning: Error Http %s, url=%s' % (e, url), file = sys.stderr)
				time.sleep(random.randint(1,3))
				retry += 1
		return page

	def check_page(self, url, page):
		if page == b'':
			return False
		return True

	def save_url(self, url, page):
		try:
			head = bytes('url: %s\npage: ' % url, encoding = 'utf-8')
			tail = b'\n~EOF!\n'
			cont = head + page + tail
		except:	
			print(traceback.print_exc(), file = sys.stderr) 
			return 0

		lock.acquire()
		self.url_num += 1
		if self.url_num % 10000 == 0:
			self.file_id += 1
			self.file_len_cur = 0
		
		fp = open('%s/%d' % (self.result_dir, self.file_id), 'ab')
		fp.write(cont)
		fp.close()

		self.file_len_cur += len(cont)
		self.file_len_total += len(cont)
		lock.release()

		return len(cont)

	def parse_link(self, ori_url, page):
		#for search results
		link_num = 0
		if ori_url.startswith('https://search.yahoo.com/search'):
			try:
				page = page.decode('utf-8')
			except:
				print('page decode failed', file = sys.stderr)

			for link in str_util.cut_windows(page, 'http%3a%2f%2f', '.pdf'):
				if link.find('<') >= 0 or link.find('>') >= 0:	
					continue
				link = 'http://%s.pdf' % link.replace('%2f', '/')
				lock.acquire()
				self.url_queue.append(link)
				#self.url_queue.append('http://' + urllib.parse.urlparse(link).netloc)
				link_num += 1
				lock.release()

		soup = BeautifulSoup(page, 'html.parser')
		for a in soup.findAll('a',href=True):
			link = a['href']
			if link != '' and link.startswith('/'):
				link = get_site(ori_url) + link
			#print('link\t%s\t%s' % (ori_url, link))
			if not self.check_link(link):
				continue
			lock.acquire()
			if len(self.url_queue) < self.queue_max_size:
				self.url_queue.append(link)
				link_num += 1
			else:	
				print('warning: queue size exceed', file = sys.stderr)
			lock.release()
	
		return link_num

	def thread_work(self, tid):
		while 1:
			print('info: t%d, url_num=%d, queue_size=%d, file_size=%d' % (tid, self.url_num, len(self.url_queue), self.file_len_total), file = sys.stderr)
			url = self.pop_url()
			print('t%d, pop_url %s' % (tid, url), file = sys.stderr)
			if url == '':
				print('trace: thread %d exit' % tid, file = sys.stderr)
				break
			
			page = self.crawl_url(url)
			print('t%d, crawl_url %s, page size=%d' % (tid, url, len(page)), file = sys.stderr)
			if not self.check_page(url, page):
				continue
		
			b_save = self.check_save(url)
			print('t%d, check_save %s, valid=%d' % (tid, url, b_save), file = sys.stderr)
			if b_save:
				len_save = self.save_url(url, page)
				print('t%d, save_url %s, size=%d' % (tid, url, len_save), file = sys.stderr)
			
			link_num = self.parse_link(url, page)
			print('t%d, parse_link %s, link_num=%d' % (tid, url, link_num), file = sys.stderr)
			if self.url_num > self.url_max_size:
				print('warning: url num exceed %d' % self.url_num, file = sys.stderr)
				break
			if self.file_len_total > self.file_max_size:
				print('warning: file size exceed %d' % self.file_len_total, file = sys.stderr)
				break
			time.sleep(random.randint(0, 5) * self.time_sleep)

	def run(self):
		threads = []
		for tid in range(self.thread_num):
			t = threading.Thread(target = self.thread_work, args = (tid, ))
			threads.append(t)
		for t in threads:
			t.start()
		for t in threads:
			t.join()


if __name__ == '__main__':
	seeds = ['http://www.xywy.com', 
		 'http://hxnk.xywy.com/fy/jc/20141023/955246.html',
		 'http://jib.xywy.com/il_sii_9900.htm?fromurl=xywyhomepage',
		 'http://healthshare.xywy.com/healthdetail/486821.htm',
		 'http://jib.xywy.com']
	white_list = [r'http://\w+.xywy.com/*']
	download_list = [r'http://\w+.xywy.com/\w+/\w+/\d+/\d+\.html', r'http://healthshare.xywy.com/healthdetail/\d+\.htm']
	sb = MiniSpider('./testdb', './testpage', seeds, 
		white_list = download_list, download_list = download_list, thread_num = 5, time_sleep = 0.1,
		queue_max_size = 1e6, url_max_size = 1e2, file_max_size = 1e9)

	if sb.prepare():
		sb.run()
	else:
		print('mini spider prepare failed', file = sys.stderr)


