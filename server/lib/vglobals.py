from os import path

import os
import tomllib

from lib import logger
from lib.listener import ConnectionTunnel

CURRENT_PATH = path.realpath(os.getcwd())
CONFIG_PATH = path.join(CURRENT_PATH, "config")
LISTENERS_PATH = path.join(CURRENT_PATH, "listeners")

SERVER_CONFIG_PATH = path.join(CONFIG_PATH, "server.toml")

if not path.exists(SERVER_CONFIG_PATH):
    logger.fatalerror(SERVER_CONFIG_PATH, "don't exist")
    quit(1)

config = tomllib.load(open(SERVER_CONFIG_PATH, "rb"))

WHITELIST: dict = config["whitelist"]
MEMORY_LIMIT: int = config["resources"]["memory_limit"] 

SSL_CERTIFICATE: str = path.join(CONFIG_PATH, config["ssl"]["certificate"])
SSL_KEY: str = path.join(CONFIG_PATH, config["ssl"]["key"])

CLIENT_SERVER_IP: str = config["client-server"]["ip"]
CLIENT_SERVER_PORT: int = config["client-server"]["port"]
CLIENT_ENABLE_SSL: bool = config["client-server"]["ssl"]

agents: dict[str, ConnectionTunnel] = {}
clients_session = {}
listeners = {}

listeners_threads = {}
listeners_available = [listener.split(".")[0] for listener in os.listdir(LISTENERS_PATH) if listener.endswith(".py")]

for k in config.keys():
    if k.startswith("listener"):
        listeners[k] = config[k]


def refresh_available_listeners():
    listeners_available.clear()
    listeners_available.extend([listener.split(".")[0] for listener in os.listdir(LISTENERS_PATH) if listener.endswith(".py")])