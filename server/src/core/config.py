from dataclasses import dataclass, field
from typing import Dict
from os import path
import tomllib

from core.paths import *
import logger

SERVER_CONFIG_PATH = path.join(CONFIG_PATH, "server.toml")

if not path.exists(SERVER_CONFIG_PATH):
    logger.fatalerror(SERVER_CONFIG_PATH, "don't exist")
    quit(1)

config = tomllib.load(open(SERVER_CONFIG_PATH, "rb"))

###########################
####### DATACLASSES #######
###########################

@dataclass
class StructSSL:
    SSL_CERTIFICATE: str 
    SSL_KEY: str

@dataclass
class StructGeneric:
    WHITELIST: Dict[str, str]
    MEMORY_LIMIT: int

@dataclass
class StructRest:
    REST_SERVER_IP: str
    REST_SERVER_PORT: int
    REST_ENABLE_SSL: bool

@dataclass
class StructWebsocket:
    WEBSOCKET_SERVER_IP: str
    WEBSOCKET_SERVER_PORT: int
    WEBSOCKET_SERVER_REDIRECT: int
    WEBSOCKET_ENABLE_SSL: bool

@dataclass
class StructJWT:
    JWT_KEY: str

###########################
####### DCLASS INIT #######
###########################

SSL = StructSSL(
    path.join(CONFIG_PATH, config["ssl"]["certificate"]),
    path.join(CONFIG_PATH, config["ssl"]["key"])
)

Generic = StructGeneric(
    config["whitelist"],
    config["resources"]["memory_limit"]
)

Rest = StructRest(
    config["rest-server"]["ip"],
    config["rest-server"]["port"],
    config["rest-server"]["ssl"],
)

Websocket = StructWebsocket(
    config["websocket-server"]["ip"],
    config["websocket-server"]["port"],
    config["websocket-server"]["redirect"],
    config["websocket-server"]["ssl"],
)

JWT = StructJWT(config["jwt"]["key"])