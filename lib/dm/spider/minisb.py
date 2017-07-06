import sys, os, time, random
import socket
import re
import leveldb
import threading
import urllib
import urllib.request
from collections import deque
from bs4 import BeautifulSoup

def get_site(url):
	try:
		r = urlparse(url)
		return r.netloc
	except:
		return ''

lock = threading.RLock()
class MiniSpider:
	def __init__(self, url_db_dir, result_dir, entry_list, white_list = [], black_list = [], 
				thread_num = 1, time_out = 1, time_sleep = 1, queue_max_size = 1e6, url_max_size = 1e7, file_max_size = 1e10):
		self.url_db_dir = url_db_dir
		self.result_dir = result_dir
		self.entry_list = entry_list
		self.white_list = white_list
		self.black_list = black_list
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
		self.url_queue = deque()
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
		while 1:	#其他进程可能在用db，所以要while try
			try:
				db = leveldb.LevelDB(self.url_db_dir)
				break
			except:
				print('db lock')
				time.sleep(random.randint(0, 10) * 0.01)
				continue
		while self.url_queue:
			url = self.url_queue.popleft()
			#print(url)
			val = ''
			try:
				val = db.Get(bytes(url, encoding = 'utf-8'))
			except:
				pass
			
			if val == '':
				new_url = url
				break

		lock.release()
		return new_url

	def check_url(self, url):
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
	
	def crawl_url(self, url):
		headers = {'User-Agent': r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
            r'Chrome/45.0.2454.85 Safari/537.36 115Browser/6.0.3',
            'Referer': r'http://www.lagou.com/zhaopin/Python/?labelWords=label',
            'Connection': 'keep-alive'
			}
		req = urllib.request.Request(url, headers = headers)
		page = ''
		try:
			page = urllib.request.urlopen(req).read()
			soup = BeautifulSoup(page, 'html.parser')
			page = page.decode(soup.original_encoding).lower()
		except Exception as e:
			print('warning: Error Http %s, url=%s' % (e, url), file = sys.stderr)
		#else:
		#	print('trace: Success, url=%s' % url, file = sys.stderr)
		return page

	def check_page(self, url, page):
		if page == '':
			return False
		return True

	def save_url(self, url, page):
		try:
			key = bytes(url, encoding = 'utf-8')
			val = bytes('%s\t%d\t%d' % (self.url_db_dir, self.file_id, self.file_len_cur), encoding = 'utf-8')
			
			head = 'url: %s\npage: ' % url
			tail = '\n~EOF!\n'
			cont = bytes(head + page + tail, encoding = 'utf-8')
		except:
			return

		lock.acquire()
		self.url_num += 1
		if self.url_num % 10000 == 0:
			self.file_id += 1
			self.file_len_cur = 0
		while 1:
			try:
				db = leveldb.LevelDB(self.url_db_dir)
				db.Put(key, val)
				break	
			except:
				print('db put failed')
				continue
		
		fp = open('%s/%d' % (self.result_dir, self.file_id), 'ab')
		fp.write(cont)
		fp.close()

		self.file_len_cur += len(cont)
		self.file_len_total += len(cont)
		lock.release()

	def parse_link(self, ori_url, page):
		soup = BeautifulSoup(page, 'html.parser')
		for a in soup.findAll('a',href=True):
			link = a['href']
			if link != '' and link.startswith('/'):
				link = get_site(ori_url) + link
			print('link\t%s\t%s' % (ori_url, link))
			if not self.check_url(link):
				continue
			lock.acquire()
			if len(self.url_queue) < self.queue_max_size:
				self.url_queue.append(link)
			else:	
				print('warning: queue size exceed', file = sys.stderr)
			lock.release()

	def thread_work(self, tid):
		while 1:
			print('info: t%d, url_num=%d, queue_size=%d, file_size=%d' % (tid, self.url_num, len(self.url_queue), self.file_len_total))
			print('t%d, pop_url...' % tid)
			url = self.pop_url()
			if url == '':
				print('trace: thread %d exit' % tid, file = sys.stderr)
				break
			
			print('t%d, crawl_url...' % tid)
			page = self.crawl_url(url)
			print('t%d, check page...' % tid)
			if not self.check_page(url, page):
				continue
			
			print('t%d, save url...' % tid)
			self.save_url(url, page)
			print('t%d, parse url...' % tid)
			self.parse_link(url, page)
			print('trace: save url %s' % url, file = sys.stderr)
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
