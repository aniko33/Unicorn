import os

from .vglobals.serverpath import LISTENERS_PATH
from .vglobals.servercfg import config
from .vglobals.sharedvars import listeners

def refresh_available_listeners():
    listeners_available.clear()
    listeners_available.extend([listener.split(".")[0] for listener in os.listdir(LISTENERS_PATH) if listener.endswith(".py")])

for k in config.keys():
    if k.startswith("listener"):
        listeners[k] = config[k]

listeners_available = [listener.split(".")[0] for listener in os.listdir(LISTENERS_PATH) if listener.endswith(".py")]