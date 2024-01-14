from lib.vglobals import *
from lib.sthread import Sthread

import rest
import hadler

import time
import resource


# Set memory limit
logger.info(f"Memory limit: {MEMORY_LIMIT}")

soft, hard = resource.getrlimit(resource.RLIMIT_AS)
resource.setrlimit(resource.RLIMIT_AS, (MEMORY_LIMIT, hard))

def loop_check_processes_listeners():
    while True:
        try:
            for listener in listeners_threads:
                listener_process: Sthread = listeners_threads[listener]

                if not listener_process.isStopped():
                    listener_process.stop()

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
            target=hadler.run,
            args=(ip, port, type))
        
        listeners_threads[listener] = thandler

        thandler.start()

    Sthread(target=loop_check_processes_listeners).start()
    
    if CLIENT_ENABLE_SSL:
        # Start rest-server with SSL
        Trest = Sthread(target=rest.run, args=(
                CLIENT_SERVER_IP,
                CLIENT_SERVER_PORT,
                True,
                (SSL_CERTIFICATE, SSL_KEY)))

    else:
        # Start rest-server without SSL
        Trest = Sthread(
            target=rest.run,
            args=(
                CLIENT_SERVER_IP,
                CLIENT_SERVER_PORT
            )
        )

    Trest.run()

if __name__ == "__main__":
    try:
        main()
    except MemoryError:
        print("Insufficient memory")
