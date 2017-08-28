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
sys.path.append('../../../alg/basic')#加入这个才能搜索到下面的
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
    while 1:    #其他进程可能在用db，所以要while try
        try:
            db = leveldb.LevelDB(db_name)
            break
        except:
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
        try:
            db = leveldb.LevelDB(db_name)
            break
        except:
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


lock = threading.RLock()  #RLock对象,是一种锁
class MiniSpider:
    def __init__(self, url_db_dir, result_dir, entry_list, white_list = [], black_list = [], download_list = [], piror_mode = 0, 
                thread_num = 1, time_out = 1, time_sleep = 1, queue_max_size = 1e6, url_max_size = 1e7, file_max_size = 1e10, debug = 0):

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
        self.debug = debug
        self.time_initial = int(time.time())
        self.url_num_last = 0
        self.old_url_queue = [] #用于存储解析的网址
        self.old_url_queue_len = 10000


    def prepare(self):
        os.system('mkdir -p %s' % self.result_dir)
        os.system('touch %s.queue' % self.url_db_dir)#如果文件存在则不覆盖
        os.system('touch %s.log' % self.url_db_dir)
        
        self.file_id = len(os.listdir(self.result_dir))
        #修复bug  从新运行程序不会新增文件夹，而是读取新文件url个数，获取url_num
        #初始化url_num值
        f = open(self.result_dir + '/' +str(len(os.listdir(self.result_dir))),'rb')
        f_line = f.readline()
        self.url_num = 0
        while f_line:
            if b'~EOF!\n' == f_line:
                self.url_num += 1
            f_line = f.readline()
        f.close()

        self.file_len_cur = 0
        self.file_len_total = 0
        socket.setdefaulttimeout(self.time_out)
        
        self.url_queue = str_util.read_lines('%s.queue' % self.url_db_dir) #所有的行读入队列url_queue中，如果断掉重新启动，队列的获取是从.queue文件中获取的
        
        for url in self.entry_list:
            self.url_queue.append(url)  #将seed加入到队尾时
        
        url_queue_len = len(self.url_queue)
        if url_queue_len > self.old_url_queue_len:
            self.old_url_queue = self.url_queue[url_queue_len - self.old_url_queue_len:url_queue_len]
        else:
            self.old_url_queue = self.url_queue
        #print("old_url_queue_len:%d" %len(self.old_url_queue))

        #todo: 判断目录是否存在
        #todo: 判断其他数值参数是否合理
        return True

    #每个线程工作过程：pop一个url，判断是否已经在db中，如果在则继续pop，直到得到或队列空；抓取，如果成功则存储并且解析超链接加入队列，否则下一次pop
    def pop_url(self):
        lock.acquire()  #和release必须成对出现,保护数据的安全
        new_url = ''
        if self.url_queue:#如果队列不为空
            if self.piror_mode == 0:#搜索的方式
                new_url = self.url_queue.pop(0)#从头弹出  宽度优先搜索
            else:
                new_url = self.url_queue.pop()#从尾弹出  深度优先搜索
        lock.release()
        return new_url

    def check_link(self, url):#检查链接是否合法
        if not (url.startswith('http://') or url.startswith('https://')):
            return False
        for pattern in self.black_list:#对于black_list中每一个链接
            if re.match(pattern, url) != None: #匹配
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

        return True    

    def crawl_url(self, url):
		#定义一个字典
        headers = {'User-Agent': r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
            r'Chrome/45.0.2454.85 Safari/537.36 115Browser/6.0.3',
            'Referer': r'http://www.lagou.com/zhaopin/Python/?labelWords=label',
            'Connection': 'keep-alive'
            }
        headers['User-Agent'] = random.choice(user_agents)
        headers['referer'] = '%d.%d.%d.%d' % (random.randint(10,100), random.randint(10,100), random.randint(10,100), random.randint(10,100))#取10,100中间的随机值
        page = b''#以二进制的方式保存
        #请求连接
        try:
            req = urllib.request.Request(url, headers = headers)
        except Exception as e:
            print('warning: Error request %s, url=%s' % (e, url), file = sys.stderr)
        
        retry = 0
        while retry < 10:
            try:#尝试读取网页数据
                page = urllib.request.urlopen(req).read()    #type(page) = bytes
                break
            except Exception as e:
                print('warning: Error Http %s, url=%s' % (e, url), file = sys.stderr)
                time.sleep(random.randint(1,3)) #等待1-3s
                retry += 1
        return page#不管成不成功，都返回page

    def check_page(self, url, page):
        if page == b'':#如果page为空，则返回错误
            return False
        return True  #否则为真

    def save_url(self, url, page):#保存网页
        try:
            head = bytes('url: %s\npage: ' % url, encoding = 'utf-8')
            tail = b'\n~EOF!\n'
            cont = head + page + tail#保存格式
        except:    
            print(traceback.print_exc(), file = sys.stderr) 
            return 0

        lock.acquire()
        self.url_num += 1

        #根据url数量在此添加函数确定速度等各项数据指标
        url_log_num = 5
        if self.url_num % url_log_num == 0:#如果url_num每增加url_log_num个，则存入文件中
            fp = open('%s.log' % self.url_db_dir, 'a')
            log_time = time.time()
            log_date = time.ctime(log_time)
            log_time_intervel = int(log_time) - self.time_initial
            fp.write('data:[%s]  url_increment:%d  time_intervel:%d  speed:%ds_perUrl\n' % (log_date,url_log_num,log_time_intervel,log_time_intervel/url_log_num))
            self.time_initial = int(log_time)
            fp.close()

        if self.url_num % 10 == 0:#如果url_num每增加10个，则存入文件中
#所有的存一次，这是慢的原因吧   清楚原始文件，再将url_queue每行存入文件。。。工作量应该很大
            fp = open('%s.queue' % self.url_db_dir, 'w')
            for url in self.url_queue:
                fp.write('%s\n' % url)
            fp.close()

        if self.url_num % 10000 == 0:#url_num每增加10000个  开辟一个新文件，且self.file_id置为0
            self.file_id += 1
            self.file_len_cur = 0
        
        fp = open('%s/%d' % (self.result_dir, self.file_id), 'ab')
        fp.write(cont)
        fp.close()

        self.file_len_cur += len(cont) #当前文件大小汇总
        self.file_len_total += len(cont) 
        lock.release()

        return len(cont)

    def parse_link(self, ori_url, page):
        #for search results
        time1 = time.time()
        new_url_list = []
        if ori_url.startswith('https://search.yahoo.com/search'):#用于检查字符串是否以指定的子字符串开头，如果是返回True
            try:
                page = page.decode('utf-8')
            except:
                print('page decode failed', file = sys.stderr)

            for link in str_util.cut_windows(page, 'http%3a%2f%2f', '.pdf'):#截取text中tag1和tag2中间的内容
                if link.find('<') >= 0 or link.find('>') >= 0:    
                    continue
                link = 'http://%s.pdf' % link.replace('%2f', '/')
                new_url_list.append(link)

        time2 = time.time()
        print('parse_link startswith time--------%f'%(time2 - time1))

        soup = BeautifulSoup(page, 'html.parser') #获取网页
        num_url_abandon  = 0
        for a in soup.findAll('a',href=True):  #获取每个网址相关的内容
            link = a['href']  #获取每个网址的url
            if link != '' and link.startswith('/'):#link出现特殊情况，需要补充完整
                link = get_site(ori_url) + link
                if not link.startswith('http:'):
                    link = 'http://' + link
            valid = self.check_link(link) #检测链接是否合法       
            if self.debug:        
                print('link\t%s\t%s\t%d' % (ori_url, link, valid), file = sys.stderr)
            if not valid:
                continue
#增加一个判断策略    过滤的网页个数
            
            if link in self.old_url_queue:
                num_url_abandon += 1
                continue
            else:
                self.old_url_queue.append(link)
                if len(self.old_url_queue) >= self.old_url_queue_len:
                    self.old_url_queue.pop(0)
                new_url_list.append(link)  #如果合法压入暂时的表中
                
        time3 = time.time()
        print('parse_link  beautifulSoup time--------%f'%(time3 - time2))
        print('abandon url num: %d  old_url_queue_num: %d'%(num_url_abandon,len(self.old_url_queue)))
        link_num = 0
        cricle_num = 0
        lock.acquire()
        for link in new_url_list:#new_url_list中的每个link
            time5 = time.time()
            url_visited = check_key(self.url_db_dir, link)
            time6 = time.time()
            cricle_num += 1
            print('parse_link_check_key num:%d_%d  time:%f  database:%d'%(cricle_num,len(new_url_list),time6 - time5,url_visited))
            if url_visited:#如果url_db_dir中存在，说明不用存储的了
                continue
            key = bytes(link, encoding = 'utf-8')
            add_kv(self.url_db_dir, key, b'')
            if len(self.url_queue) < self.queue_max_size:
                self.url_queue.append(link)#压入队列
                link_num += 1
            else:
                print('warning: queeu size exceed', file = sys.stderr)
        lock.release()
        time4 = time.time()
        print('parse_link  append time--------%f'%(time4 - time3))
        return link_num

    def get_url_log(self,time_intervel):
        lock.acquire()
        if int(time.time()) - self.time_initial >= time_intervel:
            self.time_initial = int(time.time())
            fp = open('%s.log' % self.url_db_dir, 'a')
            t = time.ctime(time.time())
            fp.write('[%s] %s %s\n' % (t,str(self.url_num),str(self.url_num - self.url_num_last)))
            self.url_num_last = self.url_num
            fp.close()
            lock.release()
            return True
        lock.release()
        return False

    def thread_work(self, tid):
        while 1:
            time_1 = time.time()
            print('info: t%d, url_num=%d, queue_size=%d, file_size=%d' % (tid, self.url_num, len(self.url_queue), self.file_len_total), file = sys.stderr)
            url = self.pop_url()  #取队列数据
            print('t%d, pop_url %s  ,time %f' % (tid, url,time.time() - time_1), file = sys.stderr) #输出到file文件中
            if url == '':#如果url为空，则认为线程退出了
                print('trace: thread %d exit' % tid, file = sys.stderr)
                break

            time_2 = time.time()
            page = self.crawl_url(url)#抓取网页
            print('t%d, crawl_url %s, page size=%d time %f' % (tid, url, len(page),time.time() - time_2), file = sys.stderr)
            if not self.check_page(url, page):#如果page为空，则跳过后面
                continue
        
            time_3 = time.time()
            b_save = self.check_save(url)#存储网页
            print('t%d, check_save %s, valid=%d time %f' % (tid, url, b_save , time.time() - time_3), file = sys.stderr)
            if b_save:
                len_save = self.save_url(url, page)
                print('t%d, save_url %s, size=%d time %f' % (tid, url, len_save,time.time() - time_3), file = sys.stderr)
            
            time_4 = time.time()
            link_num = self.parse_link(url, page)#分析页面，输入页面地址和网页内容
            print('t%d, parse_link %s, link_num=%d time %f' % (tid, url, link_num,time.time() - time_4), file = sys.stderr)
            if self.url_num > self.url_max_size:
                print('warning: url num exceed %d' % self.url_num, file = sys.stderr)
                break
            if self.file_len_total > self.file_max_size:
                print('warning: file size exceed %d' % self.file_len_total, file = sys.stderr)
                break
            time.sleep(random.randint(0, 5) * self.time_sleep)#随机sleep0-5个self_sleep的时间

    def run(self):
        threads = []
		#创建self.thread_num个线程
        for tid in range(self.thread_num):
            t = threading.Thread(target = self.thread_work, args = (tid, ))  #target是一个可调用的对象
                                                                             #调用target时的参数列表和关键词列表
            threads.append(t)
        for t in threads:
            t.start()#启动线程
        for t in threads:
            t.join()#处于阻塞模式，一直到被调线程结束


if __name__ == '__main__':
    seeds = ['http://www.xywy.com', 
         'http://hxnk.xywy.com/fy/jc/20141023/955246.html',
         'http://jib.xywy.com/il_sii_9900.htm?fromurl=xywyhomepage',
         'http://healthshare.xywy.com/healthdetail/486821.htm',
         'http://jib.xywy.com']
    white_list = [r'http://\w+.xywy.com/*']
    download_list = [r'http://\w+.xywy.com/\w+/\w+/\d+/\d+\.html', r'http://healthshare.xywy.com/healthdetail/\d+\.htm']
    sb = MiniSpider('./lichengtestdb', './lichengtestpage', seeds, 
        white_list = download_list, download_list = download_list, thread_num = 5, time_sleep = 0.1,
        queue_max_size = 1e6, url_max_size = 1e4, file_max_size = 1e9)#保存在当前目录下

    if sb.prepare():  
        sb.run() #多线程如何理解
    else:
        print('mini spider prepare failed', file = sys.stderr)


