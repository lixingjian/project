import sys, json, time
import socket
import urllib
import urllib.parse
import terminal

HOST, PORT = '10.80.28.209', 8889

listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listen_socket.bind((HOST, PORT))
listen_socket.listen(1)
print('Serving HTTP on port %s ...' % PORT, file = sys.stderr)

t = terminal.Terminal()
while True:
    try:
        client_connection, client_address = listen_socket.accept()
    except:
        time.sleep(1)
        continue

    while True:
        try:
            text = client_connection.recv(1024 * 1024).decode('utf-8')
        except:
            break
        if not text:
            break

        print(text, file = sys.stderr)
        res = {'text': 'null'}
        try:
            res = t.run(json.loads(text, encoding = 'utf-8'))
        except:
            continue
        print(res, file = sys.stderr)

        msg = json.dumps(res, ensure_ascii = False)
        client_connection.sendall(msg.encode('utf-8'))
    client_connection.close()

listen_socket.close()
