from lib import messages

from threading import Thread
from websockets.sync import client

import json
import random

# TODO: command sending

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

        Thread(target=self.get_all_messages).start()
        
    def send_chatmsg(self, msg: str):
        self.websocket.send(jsontb({"msg": msg, "auth": self.SESSION_ID, "type": "chat", "color": self.color}))
    
    def get_all_messages(self):
        for message in self.websocket:
            message = json.loads(message)
            mtype = message["type"]
            
            match mtype:
                case "chat":
                    if not message["username"] == self.username:
                        self.MAIL_COUNT += 1
                        self.MESSAGES.append(message)
                        
                        messages.info("New message arrived:", self.MAIL_COUNT)
                case "job":
                    if message["job"] in self.JOBS:
                        if message["success"]:
                            messages.green(message["output"])
                        else:
                            messages.warn(message["output"])

def random_ansi_code():
    return random.randint(31, 36)

def jsontb(__dict: dict) -> bytes:
    return json.dumps(__dict).encode()

def init_connection(url: str) -> client.ClientConnection:
    websocket = client.connect(url)

    return WSClientSession(websocket)
