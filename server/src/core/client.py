from websockets import WebSocketServerProtocol

import jwt_auth

def random_color():
    ...

class ClientSession:
    def __init__(self, token: str) -> None:

        jwt_parsed = jwt_auth.parse_jwt(token)
        
        # [ Get values from `jwt_parsed` ]

        self.username   = jwt_parsed["username"]
        self.password   = jwt_parsed["password"]
        self.session_id = jwt_parsed["session_id"]

        self.token = token
        self.color = "\033[31m"
    
    def set_websocket(self, websocket: WebSocketServerProtocol):
        self.websocket: WebSocketServerProtocol = websocket

    def is_wsclient(self) -> bool:
        return hasattr(self, "websocket")

    async def ws_close(self):
        await self.websocket.close(self.token)
        clients.remove(self.token)

    async def ws_wait_closed(self):
        await self.websocket.wait_closed()
        clients.remove(self.token)

"""
Check if a user is logged, return True if logged otherwise False  
"""
def get_user_logged(username_target: str) -> bool: # TODO optimation [no for-each]
    usernames = [client_session.username for client_session in clients.values()]

    for i, username in enumerate(usernames):
        if username == username_target:
            return i
        
    return -1

def token_exist(token: str) -> bool:
    return token in clients

"""
clients -> dict
{
    jwt -> { username, password, session_id }
    jwt: ClientSession
    
    example:
        "A.B.C": <ClientSession OBJ>
}
"""
clients: dict[str, ClientSession] = {}
