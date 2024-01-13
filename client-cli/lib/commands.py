from lib import cli as __cli

import requests as __requests
import os as __os

TARGET = []  # [ID, host]
HTTP_SESSION = __requests.session()
HTTP_POINT = ""
SESSION_ID = ""


def __get_agents() -> dict:
    r = HTTP_SESSION.get(HTTP_POINT + "/get_agents/" + SESSION_ID)

    if r.status_code != 200:
        print("ERROR:", r.text)
        return

    return r.json()


def get_agents(*args):
    agents = __get_agents()

    if len(agents) <= 0:
        print("No agents connected")
        return

    __cli.table(["ID", "Host"], agents)


def connect(*args):
    if len(args) < 1:
        print("connect <target-id>")
        return

    id_target = args[0]

    agents = __get_agents()

    for agent in agents:
        if agent[0] == id_target:
            TARGET.clear()
            TARGET.append(id_target)
            TARGET.append(agent[1])


def get_listeners(*args):
    ...


def get_ltype(*args):
    ...


def add_listener(*args):
    if len(args) < 4:
        print("add_listener <name> <ip> <port> <type>")
        return

    name = args[0]
    ip = args[1]
    port = args[2]
    type = args[3]

    r = HTTP_SESSION.post(
        HTTP_POINT + "/add_listener",
        json={"auth": SESSION_ID, "name": name, "ip": ip, "port": port, "type": type})

    if r.status_code != 200:
        print("ERROR:", r.text)
    else:
        print("Listener added:", name)


def clear(*args):
    __os.system("clear")


def quit(*args):
    print(__cli.ansi(31) + "Bye!" + __cli.reset_ansi)
    __os._exit(0)
