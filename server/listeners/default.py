import socket
import rsa

from Crypto.Cipher import Salsa20

from lib import listener
from lib import vglobals

class EncryptedTunnel(listener.ConnectionTunnel):
    def __init__(self, connection: socket.socket, agent_id: str, key: bytes, iv: bytes) -> None:
        self.key = key
        self.iv = iv

        super().__init__(connection, agent_id)

    def send(self, __data: bytes) -> int:
        cipher = Salsa20.new(self.key, self.iv)
        __data = cipher.encrypt(__data)
        
        return self.connection.send(__data)
    
    def sendall(self, __data: bytes) -> None:
        cipher = Salsa20.new(self.key, self.iv)
        __data = cipher.encrypt(__data)
        return self.connection.sendall(__data)
    
    def recv(self, __bufsize: int) -> bytes:
        __data = self.connection.recv(__bufsize)
    
        cipher = Salsa20.new(self.key, self.iv)
        return cipher.decrypt(__data)

# Entry point
def init_connection(agent: socket.socket, buffer: int):
    public, private = rsa.newkeys(1024)
    agent_id = agent.recv(buffer).decode()

    agent.send(rsa.PublicKey.save_pkcs1(public))
    
    key_iv = agent.recv(buffer)
    key_iv = rsa.decrypt(key_iv, private)

    key = key_iv[:32]
    iv = key_iv[32:]

    client_encrypted = EncryptedTunnel(agent, agent_id, key, iv)

    vglobals.agents[agent_id] = client_encrypted