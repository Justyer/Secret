import socket, time, xmlrpc.client
localip = socket.gethostbyname(socket.gethostname())
s = xmlrpc.client.ServerProxy('http://%s:6789' % (localip), allow_none=True)
time.sleep(2)
print(s.getcf())
time.sleep(2)
print(s("close")())
del s

