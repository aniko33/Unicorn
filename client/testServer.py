import socket

s = socket.socket()
s.bind(("0.0.0.0", 6666))
s.listen()

c, addr = s.accept()

print(addr)
while True:
    r = c.recv(1024)
    print(r)
    c.send(r)