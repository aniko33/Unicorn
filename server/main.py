from lib.vglobals import *

import rest
import hadler

from threading import Thread
from multiprocessing import Process

import sys
import time
import resource

# Set memory limit

logger.info(f"Memory limit: {MEMORY_LIMIT}")

soft, hard = resource.getrlimit(resource.RLIMIT_AS)
resource.setrlimit(resource.RLIMIT_AS, (MEMORY_LIMIT, hard))

def loop_check_processes_listeners():
    while True:
        try:
            for listener in LISTENERS_PROCESSES:
                listener_process: Process = LISTENERS_PROCESSES[listener]

                if not listener_process.is_alive():
                    listener_process.close()

                    listeners.pop(listener)
                    LISTENERS_PROCESSES.pop(listener)
        except RuntimeError:
            continue

        time.sleep(0.5)

def main(argc: int, argv: list[str]):
    for listener in listeners:
        ip = listeners[listener]["ip"]
        port = listeners[listener]["port"]
        type = listeners[listener]["type"]

        if not type in LISTENERS_AVAILABLE:
            logger.error(f"Listener \"{type}\" not found")
            quit(1)

        phandler = Thread( # TODO: change to multiprocessing | problem: variable mutable agents in multiprocess, does not update 
            target=hadler.run,
            args=(ip, port, type))
        
        LISTENERS_PROCESSES[listener] = phandler

        phandler.start()

    Thread(target=loop_check_processes_listeners).start()
    
    if CLIENT_ENABLE_SSL:
        # Start rest-server with SSL
        Trest = Thread(target=rest.run, args=(
                CLIENT_SERVER_IP,
                CLIENT_SERVER_PORT,
                True,
                (SSL_CERTIFICATE, SSL_KEY)))

    else:
        # Start rest-server without SSL
        Trest = Thread(
            target=rest.run,
            args=(
                CLIENT_SERVER_IP,
                CLIENT_SERVER_PORT
            )
        )

    Trest.start()

if __name__ == "__main__":
    try:
        main(len(sys.argv), sys.argv)
    except MemoryError:
        print("Insufficient memory")
