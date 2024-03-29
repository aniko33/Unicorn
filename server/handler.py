from lib import logger

import socket

from importlib import import_module

BUFFER = 1024

def use_listener(listener: str):
    return import_module("listeners." + listener)

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