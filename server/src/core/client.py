class ClientSession:
    def __init__(self, username: str, session_id: str) -> None:
        self.username   = username
        self.session_id = session_id
        
        self.websocket

"""
Check if a user is logged, return True if logged otherwise False  
"""
def get_user_logged(username_target: str) -> bool: # TODO optimation [no for-each]
    usernames = [client_session.username for client_session in clients.values()]

    for i, username in enumerate(usernames):
        if username == username_target:
            return i
        
    return -1

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
