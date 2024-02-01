from stone_color.messages import *
from stone_color.tables import ascii_table
from stone_color.color import ansistr

import requests as requests
import os as os
from pydoc import pager


# == Constants

TARGET = []  # [ID, host]
HTTP_SESSION = requests.session()
HTTP_POINT = ""
WSCONNECTION = None
USERNAME = ""
SESSION_ID = ""

##########################################################
######## Commands functions start with UPPERCASE #########
##########################################################


def _get_agents() -> dict:
    r = HTTP_SESSION.get(HTTP_POINT + "/get_agents/" + SESSION_ID)

    if r.status_code != 200:
        alertf(r.text)
        return

    return r.json()

def _get_listeners() -> dict:
    r = HTTP_SESSION.get(HTTP_POINT + "/get_listeners/" + SESSION_ID)

    if r.status_code != 200:
        alertf(r.text)
        return

    return r.json()


def Get_agents(*args):
    agents = _get_agents()

    if len(agents) <= 0:
        errorf("No agents connected")
        return

    ascii_table(["ID", "Host"], agents)



def Connect(*args):
    if len(args) < 1:
        infof("connect <target-id>")
        return

    id_target = args[0]

    agents = _get_agents()

    for agent in agents:
        if agent[0] == id_target:
            TARGET.clear()
            TARGET.extend([id_target, agent[1]])
        return

    alertf(f"Agent with ID {id_target} not found.")

def Cmd_exec(*args):
    if len(args) < 1:
        print("cmd_exec <command>")
        return
    
    if len(TARGET) <= 0:
        alertf("No target selected")
        return

    r = HTTP_SESSION.post(HTTP_POINT + "/send_command", json={"auth": SESSION_ID, "target": TARGET[0], "cmd": args[0]})
    
    if r.status_code != 200:
        alertf(r.text)
    else:
        job = r.json()["job"]
        successf("Added new job:", job)
        WSCONNECTION.JOBS.append(job)

def Listener_add(*args):
    if len(args) < 4:
        infof("listener_add <name> <ip> <port> <type>")
        return

    name = args[0]
    ip = args[1]
    port = args[2]
    type = args[3]

    r = HTTP_SESSION.post(
        HTTP_POINT + "/add_listener",
        json={"auth": SESSION_ID, "name": name, "ip": ip, "port": port, "type": type})

    if r.status_code != 200:
        alertf(r.text)
    else:
        successf("Listener added:", name)

def Listeners_get(*args):
    listeners = _get_listeners()

    if len(listeners) <= 0:
        errorf("No listeners available")
        return
    
    ascii_table(["Name", "IP", "Port", "Type"], listeners)


def Listener_type(*args):
    r = HTTP_SESSION.get(
        HTTP_POINT + "/listener_types/" + SESSION_ID)

    if r.status_code != 200:
        alertf(r.text)
    else:
        successf("Listeners:\n\t" + "\n\t".join(r.json()))


def Clear(*args):
    os.system("clear")


def Quit(*args):
    print(ansistr("Bye!", 1))
    os._exit(0)

def _slashmsg(*args):
    if len(args) < 1:
        print("/msg <text>")
        return
    
    WSCONNECTION.send_chatmsg(" ".join(args))

def _slashmail(*args):
    if len(WSCONNECTION.MESSAGES) > 0:
        messages = ["\033[{}m {}\033[0m: {}".format(msg["color"], msg["username"], msg["message"]) for msg in WSCONNECTION.MESSAGES]

        pager("\n".join(messages))
    else:
        errorf("No messages found")
