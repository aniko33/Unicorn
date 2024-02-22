from sthread import Sthread
from .config import config
from .paths import LISTENERS_PATH

import os

"""
{
    listener_name: listener_config
    example:
        "listener-alpha": {"type": "template", "ip": "0.0.0.0", "port": 7777}
}
"""
listeners = {}
listeners_threads = {}

##########################
####### Functions ########
##########################

def refresh_available_listeners():
    listeners_available_types.clear()
    listeners_available_types.extend([listener.split(".")[0] for listener in os.listdir(LISTENERS_PATH) if listener.endswith(".py")])

def add_new_listener(
        name: str,
        ip: str,
        port: int,
        type: str
    ) -> bool: # TODO: add error/exception
    
    refresh_available_listeners()
    if not type in listeners_available_types:
        return False

    listeners[name] = {"ip": ip, "port": port, "type": type}

    thread = Sthread(target=handler_run, args=(ip, port, type))

    listeners_threads[name] = thread

    return True

##########################

for k in config.keys():
    if k.startswith("listener"):
        listeners[k] = config[k]

listeners_available_types = [listener.split(".")[0] for listener in os.listdir(LISTENERS_PATH) if listener.endswith(".py")]