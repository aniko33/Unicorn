import socket
import rsa

pub, priv = rsa.newkeys(1024)

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("127.0.0.1", 9035))
s.listen()
client, addr = s.accept()

print(addr)

client.send(rsa.PublicKey.save_pkcs1(pub))
print(rsa.decrypt(client.recv(1024), priv))
print(client.recv(1024))