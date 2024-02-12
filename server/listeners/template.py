import socket
from lib.vglobals.sharedvars import agents

from api.listener import ConnectionTunnel # API import

class Tunnel(ConnectionTunnel):
    def __init__(self, connection: socket.socket, agent_id: str) -> None:
        super().__init__(connection, agent_id)

    def send(self, __data: bytes) -> int:
        return super().send(__data)

    def sendall(self, __data: bytes) -> None:
        return super().sendall(__data)

    def recv(self, __bufsize: int) -> bytes:
        return super().recv(__bufsize)

# Entry point
def init_connection(agent: socket.socket, buffer: int):
    agent_id = agent.recv(buffer).decode()

    client_conn = Tunnel(agent, agent_id)

    agents[agent_id] = client_conn
