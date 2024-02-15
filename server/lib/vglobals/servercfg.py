from os import path

from .serverpath import CONFIG_PATH
from lib import logger

import tomllib

def get_config_loaded():
    SERVER_CONFIG_PATH = path.join(CONFIG_PATH, "server.toml")
    
    if not path.exists(SERVER_CONFIG_PATH):
        logger.fatalerror(SERVER_CONFIG_PATH, "don't exist")
        quit(1)

    return tomllib.load(open(SERVER_CONFIG_PATH, "rb"))

config = get_config_loaded()

WHITELIST: dict = config["whitelist"]
MEMORY_LIMIT: int = config["resources"]["memory_limit"] 

SSL_CERTIFICATE: str = path.join(CONFIG_PATH, config["ssl"]["certificate"])
SSL_KEY: str = path.join(CONFIG_PATH, config["ssl"]["key"])

REST_SERVER_IP: str = config["rest-server"]["ip"]
REST_SERVER_PORT: int = config["rest-server"]["port"]
REST_ENABLE_SSL: bool = config["rest-server"]["ssl"]

WEBSOCKET_SERVER_IP: str = config["websocket-server"]["ip"]
WEBSOCKET_SERVER_PORT: int = config["websocket-server"]["port"]
WEBSOCKET_SERVER_REDIRECT: int = config["websocket-server"]["redirect"]
WEBSOCKET_ENABLE_SSL: bool = config["websocket-server"]["ssl"]