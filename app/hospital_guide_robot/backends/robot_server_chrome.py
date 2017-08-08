import socket
import urllib
import urllib.parse

HOST, PORT = '', 8888

listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listen_socket.bind((HOST, PORT))
listen_socket.listen(1)
print('Serving HTTP on port %s ...' % PORT, file = sys.stderr)

while True:
    client_connection, client_address = listen_socket.accept()
    request = client_connection.recv(1024).decode('gb18030')
    text = urllib.parse.unquote(request.split('\r\n')[0])

    res = 'response:'
    p1 = text.find('w=')
    p2 = text.find(' HTTP')
    if p1 < 0 or p2 < 0:
        pass
    else:
        res += text[p1+2:p2]

    http_response = """
        HTTP/1.1 200 OK
             
        %s
    """ % res

    print(http_response)
    client_connection.sendall(http_response.encode('gb18030'))
    client_connection.close()
