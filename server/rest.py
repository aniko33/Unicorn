from lib import vglobals
from hadler import run as handler_run

from flask import Flask, request, jsonify
from multiprocessing import Process
from hashlib import sha256
from uuid import uuid4

app = Flask(__name__)


@app.route("/login", methods=["POST"])
def login():
    if request.json is None:
        return "JSON body is none", 500

    username: str = request.json["username"]
    password: str = request.json["password"]

    if not username in vglobals.WHITELIST:
        return "Invalid username", 401

    orginal_password = sha256(
        vglobals.WHITELIST[username].encode()).hexdigest()

    if password != orginal_password:
        return "Invalid password", 401

    session_uuid = uuid4().hex

    vglobals.clients_session[username] = session_uuid

    return session_uuid


@app.route("/get_agents/<session>")  # type: ignore
def get_agents(session: str):
    agents = []

    if not session in list(vglobals.clients_session.values()):
        return "Invalid session ID", 401

    for agent in vglobals.agents:
        addr = vglobals.agents[agent].addr
        agents.append([agent, addr])

    return jsonify(agents)


@app.route("/add_listener", methods=["POST"])
def add_listener():
    if request.json is None:
        return "JSON body is none", 500

    session: str = request.json["auth"]

    if not session in list(vglobals.clients_session.values()):
        return "Invalid session ID", 401

    listener_type = request.json["type"]

    vglobals.refresh_available_listeners()
    if not listener_type in vglobals.LISTENERS_AVAILABLE:
        return "Invalid listener type", 403

    listener_name = request.json["name"]
    listener_ip = request.json["ip"]
    listener_port = request.json["port"]

    vglobals.listeners[listener_name] = {}
    vglobals.listeners[listener_name]["ip"] = listener_ip
    vglobals.listeners[listener_name]["port"] = listener_port
    vglobals.listeners[listener_name]["type"] = listener_type

    listener_process = Process(target=handler_run, args=(
        listener_ip, listener_port, listener_type))

    vglobals.LISTENERS_PROCESSES[listener_name] = listener_process

    return jsonify(True)


def run(ip: str, port: int, ssl=False, ssl_context=()):
    if ssl:
        app.run(ip, port, ssl_context=ssl_context)
    else:
        app.run(ip, port)
