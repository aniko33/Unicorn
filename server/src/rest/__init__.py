from .response import *
from .auth import app as auth_app
from .payload import app as payload_app
from .listener import app as listener_app

from flask import Flask

app = Flask(__name__)
app.register_blueprint(auth_app)
app.register_blueprint(payload_app)
app.register_blueprint(listener_app)

def run(ip: str, port: int, ssl=False, ssl_context=()):
    if ssl:
        app.run(ip, port, ssl_context=ssl_context)
    else:
        app.run(ip, port)

# TODO-LATER: add disconnect agent, get number of connection