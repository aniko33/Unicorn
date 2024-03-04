from core.listeners import *
from core.config import *
from core.paths import *

from sthread import Sthread
import logger

import rest
import handler
import ws_server

import time
import os
import resource

def set_memory_limit():
    logger.info(f"Memory limit: {Generic.MEMORY_LIMIT}")
    soft, hard = resource.getrlimit(resource.RLIMIT_AS)
    resource.setrlimit(resource.RLIMIT_AS, (Generic.MEMORY_LIMIT, hard))

def loop_check_thread_listeners():
    while True:
        try:
            for listener, listener_thread in listeners_threads.items():
                if listener_thread.isStopped():
                    listener_thread.stop()
                    listeners_threads.pop(listener)
        except RuntimeError:
            continue
        time.sleep(0.5)

def start_listener(ip, port, type):
    if type not in listeners_available_types:
        logger.error(f"Listener \"{type}\" not found")
        quit(1)

    thandler = Sthread(target=handler.run, args=(ip, port, type))
    listeners_threads[ip] = thandler
    thandler.start()

def start_listeners():
    for _, params in listeners.items():
        start_listener(params["ip"], params["port"], params["type"])

    Sthread(target=loop_check_thread_listeners).start()


def start_websocket():
    if Websocket.WEBSOCKET_ENABLE_SSL:
        Sthread(target=ws_server.run, args=(
            Websocket.WEBSOCKET_SERVER_IP,
            Websocket.WEBSOCKET_SERVER_PORT,
            True,
            (SSL.SSL_CERTIFICATE, SSL.SSL_KEY))
        ).start()
    else:
        Sthread(target=ws_server.run, args=(Websocket.WEBSOCKET_SERVER_IP, Websocket.WEBSOCKET_SERVER_PORT)).start()


def start_restful():
    if Rest.REST_ENABLE_SSL:
        # Start rest-server with SSL
        rest.run(
                Rest.REST_SERVER_IP,
                Rest.REST_SERVER_PORT,
                True,
                (SSL.SSL_CERTIFICATE, SSL.SSL_KEY))

    else:
        # Start rest-server without SSL
        rest.run(Rest.REST_SERVER_IP, Rest.REST_SERVER_PORT)


def main():
    # Create dist directory if it doesn't exist
    if not os.path.exists(DIST_PATH):
        os.mkdir(DIST_PATH)

    set_memory_limit()

    start_listeners()
    start_websocket()
    start_restful()

if __name__ == "__main__":
    try:
        main()
    except MemoryError:
        print("Insufficient memory")