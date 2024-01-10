from lib import commands

import readline

from os import path

CURRENT_PATH = "/".join(__file__.split("/")[:-2])
HISTORY_PATH = path.join(CURRENT_PATH, ".history")

if not path.exists(HISTORY_PATH):
    open(HISTORY_PATH, "w").close()

reset_ansi = "\033[0m"
completions = [cmd for cmd in dir(commands) if not cmd.startswith("__") | cmd.isupper()]

def _readline_completer(text: str, state):
    if text:
        matches = [s for s in completions if s and s.startswitch(text)]
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



def ansi(code: int, style = 38) -> str:
    return f"\033[{style};5;{code}m"

def preinput() -> str:
    return readline.get_line_buffer()

def iinput(__prompt: str) -> tuple:
    getted = input(__prompt)

    readline.write_history_file(HISTORY_PATH)

    return getted.split()

def table(headers: list, rows: list, style_c="-", spaced=2):
    # Calculates the maximum width for each column
    max_widths = [len(header) for header in headers]
    for row in rows:
        if len(row) != len(headers):
            raise
        for i, cell in enumerate(row):
            max_widths[i] = max(max_widths[i], len(cell))

    print()

    if spaced <= 0:
        # Priting headers and separators
        print(
            "\t".join(
                "{0:{1}}".format(header, max_widths[i])
                for i, header in enumerate(headers)
            )
        )
        print("\t".join(style_c * width for width in max_widths))

        # Priting rows
        for row in rows:
            print(
                "\t".join(
                    "{0:{1}}".format(cell, max_widths[i]) for i, cell in enumerate(row)
                )
            )
    else:
        # Priting headers and separators
        print(
            (" " * spaced)
            + (
                "\t".join(
                    "{0:{1}}".format(header, max_widths[i])
                    for i, header in enumerate(headers)
                )
            )
        )
        print((" " * spaced) + ("\t".join(style_c * width for width in max_widths)))

        for row in rows:
            # Priting rows
            print(
                (" " * spaced)
                + (
                    "\t".join(
                        "{0:{1}}".format(cell, max_widths[i])
                        for i, cell in enumerate(row)
                    )
                )
            )

    print()

