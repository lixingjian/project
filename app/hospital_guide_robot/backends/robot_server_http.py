#!coding=UTF-8    
from http.server import HTTPServer,BaseHTTPRequestHandler     
import io,shutil,urllib     
import sys, json, time
import socket
import terminal

input_test = '{"user":{"uid":1, "name":"dingdang", "sex":1, "age":32}, "request":{"serv": 0, "text":"头痛挂什么科", "type":0, "time":99}}'
t = terminal.Terminal()     
class MyHttpHandler(BaseHTTPRequestHandler):     
    def do_GET(self):     
        rq = ''
        msg = ''
        if '?' in self.path:#如果带有参数     
            self.queryString = urllib.parse.unquote(self.path.split('?',1)[1])     
            params = urllib.parse.parse_qs(self.queryString)     
            if 'rq' in params:
                rq = params['rq'][0]
            print(params)
        
        res = {'text': 'null'}
        try:
            print(rq)
            js = json.loads(rq, encoding = 'gb18030')
            print(js)
            res = t.run(js)
            msg = json.dumps(res, ensure_ascii = False)
        except:
            print(sys.exc_info()[0],sys.exc_info()[1])
        
        print(res, file = sys.stderr)
        
        enc = 'utf-8' 
        r_str = msg
        encoded = ''.join(r_str).encode('utf-8')     
        f = io.BytesIO()     
        f.write(encoded)     
        f.seek(0)     
        self.send_response(200)     
        self.send_header("Content-type", "text/html; charset=%s" % enc)     
        self.send_header("Content-Length", str(len(encoded)))     
        self.end_headers()     
        shutil.copyfileobj(f,self.wfile)     

    def do_POST(self):     
        s=str(self.rfile.readline(),'UTF-8')#先解码     
        print(urllib.parse.parse_qs(urllib.parse.unquote(s)))#解释参数     
        self.send_response(301)#URL跳转     
        self.send_header("Location", "/?"+s)     
        self.end_headers()     
    
httpd=HTTPServer(('',8080),MyHttpHandler)     
print("Server started on 127.0.0.1,port 8080.....")     
httpd.serve_forever()  
