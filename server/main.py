from lib.vglobals import *

import rest
import hadler

from threading import Thread
from multiprocessing import Process

import sys
import resource

# Set memory limit

soft, hard = resource.getrlimit(resource.RLIMIT_AS)
resource.setrlimit(resource.RLIMIT_AS, (MEMORY_LIMIT, hard))

def main(argc: int, argv: list[str]):

    for listener in LISTENERS:
        ip = LISTENERS[listener]["ip"]
        port = LISTENERS[listener]["port"]
        type = LISTENERS[listener]["type"]

        phandler = Process  (
            target=hadler.run,
            args=(ip, port, type))
        
        LISTENERS_PROCESSES[listener] = phandler

        phandler.start()

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
