from os import path
import importlib.util
import socket

from core.paths import LISTENERS_PATH
import logger

BUFFER = 1024

def use_listener(listener: str):
    spec = importlib.util.spec_from_file_location(listener, path.join(LISTENERS_PATH, listener + ".py"))
    listener_loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(listener_loaded)
    return listener_loaded

def run(ip: str, port: int, listener_type: str):
    module = use_listener(listener_type)
    entry = getattr(module, "init_connection")

    server = socket.socket()
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server.bind((ip, port))
    server.listen()

    logger.debug(f"{listener_type}: Listening in {ip}:{port}")

    while True:
        agent, addr = server.accept()
        logger.info("Agent connected: " + str(addr))
        
        entry(agent, BUFFER)