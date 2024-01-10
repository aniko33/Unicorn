from lib import vglobals

from flask import Flask, request, jsonify
from hashlib import sha256
from uuid import uuid4

app = Flask(__name__)

@app.route("/login", methods=["POST"])
def login():
    username: str = request.json["username"] # type: ignore
    password: str = request.json["password"] # type: ignore
    
    if not username in vglobals.WHITELIST:
        return "Invalid username", 401
    
    orginal_password = sha256(vglobals.WHITELIST[username].encode()).hexdigest()
    
    if password != orginal_password:
        print(password, orginal_password)
        return "Invalid password", 401
    
    session_uuid = uuid4().hex
    
    vglobals.servercfg.clients_session[username] = session_uuid

    return session_uuid

@app.route("/get_agents/<session>") # type: ignore
def get_agents(session: str):
    agents = []
    
    if not session in list(vglobals.servercfg.clients_session.values()):
        return "Invalid session ID", 401
    
    for agent in vglobals.servercfg.agents:
        print(vglobals.servercfg.agents[agent])
        addr = vglobals.servercfg.agents[agent].addr
        agents.append([agent, addr])

    return jsonify(agents)

def add_listener():
    ...

def run(ip: str, port: int, ssl = False, ssl_context = ()):
    if ssl:
        app.run(ip, port, ssl_context = ssl_context)
    else:
        app.run(ip, port)