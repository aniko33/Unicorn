from stone_color.messages import *

from threading import Thread
from websockets.sync import client
from websockets import exceptions as websocket_exceptions

import json
import random

class WSClientSession:
    def __init__(self, websocket_connection: client.ClientConnection) -> None:
        from lib.commands import SESSION_ID, USERNAME as username

        self.SESSION_ID = SESSION_ID
        self.MAIL_COUNT = 0
        self.MESSAGES: list[dict] = []
        self.JOBS = []
        
        self.username = username
        self.color = random_ansi_code() # Username color
        self.websocket = websocket_connection

        Thread(target=self.excepted_get_all_messages).start()

    def sync_chat(self):
        self.websocket.send(jsontb({"auth": self.SESSION_ID}, "sync"))

    def send_chatmsg(self, msg: str):
        self.websocket.send(jsontb({"msg": msg, "color": self.color, "auth": self.SESSION_ID}, "chat"))

    def send_command(self, cmd: str, target_id: str):
        self.websocket.send(jsontb({"exec": cmd, "target": target_id, "auth": self.SESSION_ID}, "send_command"))
    
    def excepted_get_all_messages(self):
        try:
            self._get_all_messages()
        except websocket_exceptions.ConnectionClosedError:
            # TODO: do reconnection
            alertf("Server disconnected")

    def _get_all_messages(self):
        for message in self.websocket:
            message: dict = json.loads(message)
            mtype = message["type"]
            
            match mtype:
                case "chat":
                    if not message["username"] == self.username:
                        self.MAIL_COUNT += 1

                    # Remove useless information
                    message.pop("status")
                    message.pop("type")

                    self.MESSAGES.append(message)

                case "job":
                    if message["job"] in self.JOBS:
                        if message["success"]:
                            successf(message["output"])
                        else:
                            successf(message["output"])
                
                case "sync":
                    self.MESSAGES.extend(message["messages"])

                case "send_command":
                    if message["status"] != 200:
                        alertf(message)
                    else:
                        job = message["job"]
                        successf("Added new job:", job)
                        self.JOBS.append(job)

def random_ansi_code():
    return random.randint(31, 36)

def jsontb(__dict: dict, type: str) -> bytes:
    __dict.update({"type": type})
    
    return json.dumps(__dict).encode()

def init_connection(url: str) -> client.ClientConnection:
    websocket = client.connect(url)

    return WSClientSession(websocket)
