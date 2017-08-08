import sys, json, random
import socket
import urllib
import urllib.parse
import terminal

import socket
import copy

sex_str = ['女', '男']
user_list = [(1, 'Tom', 1, 2), (2, 'Bill', 1, 65), (3, 'Lucy', 0, 28)]
uid = random.randint(0, 2)
iters = random.randint(1, 5)
def fake_input(buf, uid = 0):
    request = copy.deepcopy(terminal.request_template)
    user_info = request['user']
    if uid == 0:
        user_info['uid'], user_info['name'], user_info['sex'], user_info['age'] = random.choice(user_list)
    else:
        user_info['uid'], user_info['name'], user_info['sex'], user_info['age'] = user_list[uid - 1]
    request['request']['text'] = buf.strip()
    request['request']['type'] = 0
    return request

sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sk.connect(('10.80.28.209', 8888))  # 主动初始化与服务器端的连接

while 1:
    try:
        buf = input().rstrip()
    except:
        break
    if iters == 0:
        uid = random.randint(0, 2)
        iters = random.randint(1, 5)
    request = fake_input(buf, uid)    
    print(request)
    sk.sendall(bytes(json.dumps(request, ensure_ascii = False), encoding = 'utf-8'))
    res = sk.recv(1024 * 1024)
    print(str(res, encoding = 'utf-8'))
    iters -= 1

