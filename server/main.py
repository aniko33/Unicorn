from lib.vglobals.servercfg import *
from lib.vglobals.sharedvars import listeners_threads, listeners
from lib.globals import listeners_available

from lib.sthread import Sthread
from lib import logger

import rest
import handler
import wserver

import time
import resource

# Set memory limit

logger.info(f"Memory limit: {MEMORY_LIMIT}")

soft, hard = resource.getrlimit(resource.RLIMIT_AS)
resource.setrlimit(resource.RLIMIT_AS, (MEMORY_LIMIT, hard))

def loop_check_thread_listeners():
    while True:
        try:
            for listener in listeners_threads:
                listener_thread: Sthread = listeners_threads[listener]

                if listener_thread.isStopped():
                    listener_thread.stop()

                    listeners.pop(listener)
                    listeners_threads.pop(listener)
        except RuntimeError:
            continue

        time.sleep(0.5)

def main():
    for listener in listeners:
        ip = listeners[listener]["ip"]
        port = listeners[listener]["port"]
        type = listeners[listener]["type"]

        if not type in listeners_available:
            logger.error(f"Listener \"{type}\" not found")
            quit(1)

        thandler = Sthread(
            target=handler.run,
            args=(ip, port, type))
        
        listeners_threads[listener] = thandler

        thandler.start()

    Sthread(target=loop_check_thread_listeners).start()
    
    if WEBSOCKET_ENABLE_SSL:
        Sthread(target=wserver.run, args=(
            WEBSOCKET_SERVER_IP,
            WEBSOCKET_SERVER_PORT,
            True,
            (SSL_CERTIFICATE, SSL_KEY))
        ).start()
    else:
        Sthread(target=wserver.run, args=(WEBSOCKET_SERVER_IP, WEBSOCKET_SERVER_PORT)).start()


    if REST_ENABLE_SSL:
        # Start rest-server with SSL
        rest.run(
                REST_SERVER_IP,
                REST_SERVER_PORT,
                True,
                (SSL_CERTIFICATE, SSL_KEY))

    else:
        # Start rest-server without SSL
        rest.run(REST_SERVER_IP,REST_SERVER_PORT)

if __name__ == "__main__":
    try:
        main()
    except MemoryError:
        print("Insufficient memory")
