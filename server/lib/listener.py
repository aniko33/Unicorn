import socket
import time

from threading import Thread
from abc import ABC, abstractmethod

from lib.vglobals.sharedvars import agents

class ConnectionTunnel(ABC):
    def __init__(self, connection: socket.socket, agent_id: str) -> None:
        self.connection = connection
        self.agent_id = agent_id
        
        addr = connection.getpeername()

        self.addr = addr[0] + ":" + str(addr[1])

        Thread(target=self.__stayalive).start()
    
    @abstractmethod
    def send(self, __data: bytes) -> int:
        return self.connection.send(__data)

    @abstractmethod
    def sendall(self, __data: bytes) -> None:
        return self.connection.sendall(__data)
    
    @abstractmethod
    def recv(self, __bufsize: int) -> bytes:
        return self.connection.recv(__bufsize)
    
    def __stayalive(self):
        is_alive = True

        while is_alive:
            time.sleep(10)

            try:
                self.send(b"2")
                data = self.connection.recv(16, socket.MSG_DONTWAIT | socket.MSG_PEEK)

                if len(data) == 0:
                    is_alive = False
            
            except ConnectionResetError:
                is_alive = False

            except BrokenPipeError:
                is_alive = False

            except BlockingIOError:
                ...
        
        if not is_alive:
            agents.pop(self.agent_id)