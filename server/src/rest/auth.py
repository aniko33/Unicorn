from functools import wraps
from flask import Blueprint, request, jsonify
import uuid
import hashlib

from . import response
from core.client import clients, get_user_logged, ClientSession
from core.config import StructWebsocket
from core.config import StructGeneric
import jwt_auth

app = Blueprint("auth", __name__)

def reserved_api(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        key = request.headers.get("key")

        if not key:
            return response.sessionid_not_found
        
        if not key in list(clients.values()):
            return response.invalid_sessionid
        else:
            return func(*args, **kwargs) 
    
    return decorated

@app.route("/login", methods=["POST"])
def login():
    rdict = request.get_json()
    username = rdict["username"]
    password = rdict["password"]

    if not username in StructGeneric.WHITELIST:
        return response.username_is_not_whitelisted

    orginal_password = hashlib.sha256(
        StructGeneric.WHITELIST[username].encode()).hexdigest()

    if password != orginal_password:
        return response.invalid_password

    # [ Remove old session user ]

    index = get_user_logged(username)

    if index >= 0:
        clients.pop(clients[index])

    # [ Generate session_id & create JWT token ]

    session_id = uuid.uuid4()
    token = jwt_auth.gen_jwt(username, password, session_id)
    
    clients[token] = ClientSession(username, session_id)

    return jsonify({"token": token, "wsaddr": StructWebsocket.WEBSOCKET_SERVER_REDIRECT})
