import uuid

class HTTP_SESSION:
    def __init__(self) -> None:
        self.sessions: dict[str, str] = {}

    def add_session(self, ip: str | None):
        if ip is None:
            return False
        else:
            session = uuid.uuid4().hex
            self.sessions[ip] = session
            return True, session
        
    def remove_session(self, session):
        ip = list(self.sessions.keys())[list(self.sessions.values()).index(session)]
        self.sessions.pop(ip)

    def check(self, ip, session) -> bool:
        if session == self.sessions[ip]:
            return True
        else:
            return False

# TODO: do optimation

def get_tunnel_by_fingerprint(agents: dict, fingerprint: str) -> str | None:
    i = 0

    for v in list(agents.values()):
        if fingerprint == v:
            return list(agents.keys())[i]
        i+=1
    
    return None