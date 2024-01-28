from lib import cli as __cli
from lib import messages as __msg

import requests as __requests
import os as __os

# == Constants

TARGET = []  # [ID, host]
HTTP_SESSION = __requests.session()
HTTP_POINT = ""
WSCONNECTION = None
USERNAME = ""
SESSION_ID = ""


def __get_agents() -> dict:
    r = HTTP_SESSION.get(HTTP_POINT + "/get_agents/" + SESSION_ID)

    if r.status_code != 200:
        __msg.alert(r.text)
        return

    return r.json()

def __get_listeners() -> dict:
    r = HTTP_SESSION.get(HTTP_POINT + "/get_listeners/" + SESSION_ID)

    if r.status_code != 200:
        __msg.alert(r.text)
        return

    return r.json()


def get_agents(*args):
    agents = __get_agents()

    if len(agents) <= 0:
        __msg.red("No agents connected")
        return

    __cli.table(["ID", "Host"], agents)


def get_listeners(*args):
    listeners = __get_listeners()

    if len(listeners) <= 0:
        __msg.red("No listeners available")
        return
    
    __cli.table(["Name", "IP", "Port", "Type"], listeners)


def connect(*args):
    if len(args) < 1:
        __msg.info("connect <target-id>")
        return

    id_target = args[0]

    agents = __get_agents()

    for agent in agents:
        if agent[0] == id_target:
            TARGET.clear()
            TARGET.extend([id_target, agent[1]])

def cmd_exec(*args):
    if len(args) < 1:
        print("cmd_exec <command>")
        return
    
    if len(TARGET) <= 0:
        __msg.alert("No target selected")
        return

    r = HTTP_SESSION.post(HTTP_POINT + "/send_command", json={"auth": SESSION_ID, "target": TARGET[0], "cmd": args[0]})
    
    if r.status_code != 200:
        __msg.alert(r.text)
    else:
        job = r.json()["job"]
        __msg.green("Added new job:", job)
        WSCONNECTION.JOBS.append(job)

def get_ltype(*args):
    ...

def add_listener(*args):
    if len(args) < 4:
        __msg.info("add_listener <name> <ip> <port> <type>")
        return

    name = args[0]
    ip = args[1]
    port = args[2]
    type = args[3]

    r = HTTP_SESSION.post(
        HTTP_POINT + "/add_listener",
        json={"auth": SESSION_ID, "name": name, "ip": ip, "port": port, "type": type})

    if r.status_code != 200:
        __msg.alert(r.text)
    else:
        __msg.green("Listener added:", name)


def clear(*args):
    __os.system("clear")


def quit(*args):
    print(__cli.ansi(31) + "Bye!" + __cli.reset_ansi)
    __os._exit(0)


def _slashmsg(*args):
    if len(args) < 1:
        print("/msg <text>")
        return
    
    WSCONNECTION.send_chatmsg(" ".join(args))

def _slashmail(*args):
    if len(WSCONNECTION.MESSAGES) > 0:
        messages = ["\033[{}m {}\033[0m: {}".format(msg["color"], msg["username"], msg["message"]) for msg in WSCONNECTION.MESSAGES]

        __cli.pager("\n".join(messages))
    else:
        __msg.red("No messages found")
