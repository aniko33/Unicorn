import socket
import json
import io

from lib.vglobals.sharedvars import agents
from lib.response import wresponse

from api.listener import * # API import

class Tunnel(ConnectionTunnel):
    def __init__(self, connection: socket.socket, agent_id: str) -> None:
        super().__init__(connection, agent_id)

        Thread(target=self.__broadcast).start()

    def send_command(self, cmd: str, job: int) -> int:
        return super().send_command(cmd, job)

    def send(self, __data: bytes) -> int:
        return super().send(__data)

    def sendall(self, __data: bytes) -> None:
        return super().sendall(__data)

    def recv(self, __bufsize: int) -> bytes:
        return super().recv(__bufsize)
    
    def recvall(self, __bufsize: int) -> bytes:
        return super().recvall(__bufsize)
    
    def __broadcast(self):
        while True:
            r = self.recv(1024)
            if len(r) <= 0:
                self.connection.close()
                agents.pop(self.agent_id)
                return
            
            r = json.loads(r)      # Trasform to JSON format

            rtype = r["type"]      # Get type of request
            success = r["success"] # Get status of request

            match rtype:           # Matches of any types
                case "cmdout":
                    send_to_all_clients(wresponse(r, "job"))

                case "download":
                    if not success:
                        continue

                    self.send(b"1")

                    with io.BytesIO() as f:
                        while True:
                            packet = self.recv(1024)
                            f.write(packet)

                            if len(packet) < 1024:
                                break

# Entry point
def init_connection(agent: socket.socket, buffer: int):
    agent_id = agent.recv(buffer).decode()

    client_conn = Tunnel(agent, agent_id)

    agents[agent_id]["connection"] = client_conn
