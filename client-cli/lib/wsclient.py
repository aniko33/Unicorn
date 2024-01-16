from lib import messages

from threading import Thread
from websockets.sync import client

import json

# TODO: implements mail-box and command sending

class WSClientSession:
    def __init__(self, websocket_connection: client.ClientConnection) -> None:
        from lib.commands import SESSION_ID, USERNAME

        self.SESSION_ID = SESSION_ID
        self.USERNAME = USERNAME
        self.MAIL_COUNT = 0
        self.MESSAGES: list[dict] = []

        self.websocket = websocket_connection

        Thread(target=self.get_all_messages).start()
        
    def send_chatmsg(self, msg: str):
        self.websocket.send(jsontb({"msg": msg, "auth": self.SESSION_ID, "type": "chat"}))
    
    def send_command(self, cmd: str, target: str):
        self.websocket.send(jsontb({"exec": cmd, "target": target, "auth": self.SESSION_ID, "type": "cmd"}))

    def get_all_messages(self):
        for message in self.websocket:
            message = json.loads(message)
            mtype = message["type"]
            
            match mtype:
                case "chat":
                    if not message["username"] == self.USERNAME:
                        self.MAIL_COUNT += 1
                        self.MESSAGES.append(message)
                        
                        messages.info("New message arrived:", self.MAIL_COUNT, start="\n")

def jsontb(__dict: dict) -> bytes:
    return json.dumps(__dict).encode()

def init_connection(url: str) -> client.ClientConnection:
    websocket = client.connect(url)

    return WSClientSession(websocket)
