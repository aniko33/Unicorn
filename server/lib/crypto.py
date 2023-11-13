import os
import socket

from Crypto.Cipher import Salsa20

class EncryptedTunnel:
    def __init__(self, stream_socket: socket.socket, key: bytes, nonce: bytes) -> None:
        self.key = key
        self.nonce = nonce

        self.socket: socket.socket = stream_socket

    def send(self, data: bytes):
        cipher = Salsa20.new(self.key, self.nonce)

        self.socket.send(cipher.encrypt(data))

    def recv(self, buffer: int) -> bytes:
        cipher = Salsa20.new(self.key, self.nonce)

        data = self.socket.recv(buffer)
        return cipher.decrypt(data)
    
    def recv_big(self, buffer: int) -> bytearray:
        data = bytearray()
        
        while True:
            recved = self.recv(buffer)
            data.extend(recved)
            if len(recved) < buffer:
                break

        return data
    
def get_hwid() -> str:
    if os.name == "nt":
        import subprocess
        return subprocess.getoutput("wmic csproduct get uuid")        
    else:
        return open("/etc/machine-id", "r").read().strip()