from lib import commands

from stone_color.color import ansistr, legacy_ansistr
from os import path
from pydoc import pager

import readline

CURRENT_PATH = "/".join(__file__.split("/")[:-2])
HISTORY_PATH = path.join(CURRENT_PATH, ".history")
SPECIAL_PREFIX = {"_dot": ".", "_slash": "/", "_colon": ":", "_dot": "."}

if not path.exists(HISTORY_PATH):
    open(HISTORY_PATH, "w").close()

def _is_command_case(text: str) -> bool:
    return text[0].isupper() and text[1:].islower()

def _to_command_case(text: str) -> bool:
    return text[0].upper() + text[1:].lower()

def _to_special_case(text: str):
    for word, initial in SPECIAL_PREFIX.items():
        text = text.replace(word, initial)

    return text

def _from_special_case(text: str):
    special_prefix_inveted = {v: k for k, v in SPECIAL_PREFIX.items()}.items()

    for word, initial in special_prefix_inveted:
        text = text.replace(word, initial)

    return text


completions = [cmd.lower() for cmd in dir(commands) if _is_command_case(cmd) and not cmd.startswith(tuple(SPECIAL_PREFIX.keys()))]
special_completions = [_to_special_case(cmd) for cmd in dir(commands) if cmd.startswith(tuple(SPECIAL_PREFIX.keys()))]

completions.extend(special_completions)

def _readline_completer(text: str, state):
    if text:
        matches = [s for s in completions if s and s.startswith(text)]
    else:
        matches = completions[:]

    try:
        return matches[state]
    except IndexError:
        return None


def _readline_start():
    readline.read_history_file(HISTORY_PATH)
    readline.set_completer(_readline_completer)
    readline.parse_and_bind("tab: complete")


def preinput() -> str:
    return readline.get_line_buffer()


def iinput() -> tuple:
    prompt = legacy_ansistr("unicorn", 4)

    if len(commands.TARGET) > 0:
        ip, port = commands.TARGET[1].split(':')
        getted = input(f"{prompt} [ {ip}:{ansistr(port, 1)} ] :: ")
    else:
        getted = input(f"{prompt} :: ")

    readline.write_history_file(HISTORY_PATH)

    return getted.split()