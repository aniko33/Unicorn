import socket
import json
import asyncio

from threading import Thread
from abc import ABC, abstractmethod

from lib.vglobals.sharedvars import agents, clients_wsocket
from lib.response import wresponse

class ConnectionTunnel(ABC):
    def __init__(self, connection: socket.socket, agent_id: str) -> None:
        self.connection = connection
        self.agent_id = agent_id
        
        addr = connection.getpeername()

        self.addr = addr[0] + ":" + str(addr[1])

        Thread(target=self.__broadcast).start()
    
    @abstractmethod
    def send(self, __data: bytes) -> int:
        return self.connection.send(__data)

    @abstractmethod
    def sendall(self, __data: bytes) -> None:
        return self.connection.sendall(__data)
    
    @abstractmethod
    def recv(self, __bufsize: int) -> bytes:
        return self.connection.recv(__bufsize)
    
    def __broadcast(self): # TODO: implement auto-add comamnd (client), upload, download
        while True:
            r = self.recv(1024)
            if len(r) <= 0:
                self.connection.close()
                agents.pop(self.agent_id)
                return

            r = json.loads(r)

            for connection in clients_wsocket:
                asyncio.run(connection.send(wresponse(r, "job")))
