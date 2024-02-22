from flask import Blueprint, request, send_file, jsonify
from os import path
import os
import importlib
import inspect


from . import  response
from core.paths import DIST_PATH
from .auth import reserved_api

app = Blueprint("payload", __name__)

@app.route("/payload_generate", methods=["POST"])
@reserved_api
def payload_generate():
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
    payload_builder = importlib.import_module(".".join(("payload", payload_name, "setup")))
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

@app.route("/payload_download/filename", methods=["GET"])
@reserved_api
def payload_download(filename):
    payload_filename = path.join(DIST_PATH, path.basename(filename))
    
    if not path.exists(payload_filename):
        return response.payload_not_found
    
    return send_file(payload_filename) 

@app.route("/payload_files")
@reserved_api
def payload_files():
    return jsonify(os.listdir(DIST_PATH))

@app.route("/payload_get")
@reserved_api
def payload_get():
    return os.listdir(path.join("payload"))

@app.route("/payload_config", methods=["POST"])
@reserved_api
def payload_config():
    payload_name: str = request.json["payload"]

    if not path.exists(path.join("payload", payload_name)):
        return response.payload_not_found
    
    payload_builder = importlib.import_module(".".join(("payload", payload_name, "setup")))
    config_obj = getattr(payload_builder.Config, "run")

    parameters = [] # name, is_required

    for parameter in inspect.signature(config_obj).parameters.values():
        if parameter.name == "self":
            continue
        
        is_required = isinstance(parameter.default(), inspect._empty)
        
        parameters.append([parameter.name, is_required])

    return jsonify(parameters)