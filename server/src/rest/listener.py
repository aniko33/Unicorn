from flask import Blueprint, request, jsonify

from core.listeners import *
from .auth import reserved_api

app = Blueprint("listener", __name__)

@app.route("/add_listener", methods=["POST"])
@reserved_api
def add_listener():
    listener_type = request.json["type"]
    listener_name: str = request.json["name"]
    listener_ip: str = request.json["ip"]
    listener_port: int = request.json["port"]

    if not add_new_listener(
        listener_name,
        listener_ip,
        listener_port,
        listener_type):
        
        return "Invalid listener type", 403

    return jsonify(True)

@app.route("/get_listeners")
@reserved_api
def get_listeners():
    listeners_row = []

    for listener_name in listeners:
        listener = listeners[listener_name]
        
        ip = listener["ip"]
        port = listener["port"]
        type = listener["type"]
        listeners_row.append([listener_name, ip, port, type])

    return jsonify(listeners_row)

@app.route("/listener_types")
@reserved_api
def get_listeners_types():
    return jsonify(listeners_available_types)
