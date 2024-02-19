import socket
import json
import asyncio

from threading import Thread
from abc import ABC, abstractmethod

from lib.vglobals.sharedvars import agents, clients_wsocket
from lib.response import wresponse

def send_to_all_clients(msg: str):
    for connection in clients_wsocket:
        asyncio.run(connection.send(msg))

class ConnectionTunnel(ABC):
    def __init__(self, connection: socket.socket, agent_id: str) -> None:
        self.connection = connection
        self.agent_id = agent_id
        
        addr = connection.getpeername()

        self.addr = addr[0] + ":" + str(addr[1])

        # ! Thread(target=self.__broadcast).start()
    
    @abstractmethod
    def send_command(self, cmd: str, job: int) -> int:
        cmd_json = json.dumps({"exec": cmd, "job": job})
        return self.connection.send(cmd_json.encode())

    @abstractmethod
    def send(self, __data: bytes) -> int:
        return self.connection.send(__data)

    @abstractmethod
    def sendall(self, __data: bytes) -> None:
        return self.connection.sendall(__data)
    
    @abstractmethod
    def recv(self, __bufsize: int) -> bytes:
        return self.connection.recv(__bufsize)
    
    @abstractmethod
    def recvall(self, __bufsize: int) -> bytes:
        buffer = bytearray()
        while True:
            frame = self.recv(__bufsize)
            buffer.extend(frame)
            if len(frame) < __bufsize: break
    
        return bytes(buffer)

    def __broadcast(self): # TODO: implement auto-add comamnd (client)
        while True:
            r = self.recv(1024)
            if len(r) <= 0:
                self.connection.close()
                agents.pop(self.agent_id)
                return

            print(r)