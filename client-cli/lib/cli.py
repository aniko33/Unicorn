from lib import commands
from lib.messages import ansi, ansi_str, reset_ansi

from os import path
from pydoc import pager

import readline

CURRENT_PATH = "/".join(__file__.split("/")[:-2])
HISTORY_PATH = path.join(CURRENT_PATH, ".history")
SPECIAL_PREFIX = {"_dot": ".", "_slash": "/", "_colon": ":"}

if not path.exists(HISTORY_PATH):
    open(HISTORY_PATH, "w").close()


def _to_special_case(text: str):
    for word, initial in SPECIAL_PREFIX.items():
        text = text.replace(word, initial)

    return text


def _from_special_case(text: str):
    special_prefix_inveted = {v: k for k, v in SPECIAL_PREFIX.items()}.items()

    for word, initial in special_prefix_inveted:
        text = text.replace(word, initial)

    return text


completions = [cmd for cmd in dir(commands) if not cmd.startswith("__") | cmd.isupper() | cmd.startswith(tuple(SPECIAL_PREFIX.keys()))]
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
    prompt = ansi_str("unicorn", 4)

    if len(commands.TARGET) > 0:
        ip, port = commands.TARGET[1].split(':')
        getted = input(f"{prompt} [ {ip}:{ansi_str(port, 31)} ] :: ")
    else:
        getted = input(f"{prompt} :: ")

    readline.write_history_file(HISTORY_PATH)

    return getted.split()


def table(headers: list[str], data: list[list[str]], spaces=4, lspace=3):
    div = " "*spaces
    ldiv = " "*lspace

    print()

    col_widths = [max(len(str(cell)) for cell in col) for col in zip(headers, *data)]

    header_row = div.join(f"{header: <{width}}" for header, width in zip(headers, col_widths))
    print(ldiv + header_row)

    separator_row = div.join("-" * width for width in col_widths)
    print(ldiv + separator_row)

    for row in data:
        row_str = div.join(f"{cell: <{width}}" for cell, width in zip(row, col_widths))
        print(ldiv + row_str)

    print()
