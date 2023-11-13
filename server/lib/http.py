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

    def exist(self, ip, session) -> bool:
        if session == self.sessions[ip]:
            return True
        else:
            return False

def get_agent_by_fingerprint(agents: dict, fingerprint: str) -> str | None:
    agents_values = list(agents.values())

    if len(agents_values) <= 0:
        return None
    
    low = 0
    high = len(agents.values())
    
    r = None
    
    while low<=high:
        mid = (low + high) // 2

        if agents_values[mid][0].decode() < fingerprint:
            low = mid + 1
        
        elif agents_values[mid][0].decode() > fingerprint:
            high = mid - 1
        
        else:
            r = mid
            break

    if r != None:
        return list(agents.keys())[r]
    else:
        return None