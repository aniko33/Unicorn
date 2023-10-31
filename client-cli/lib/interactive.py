import readline
import os

CURRENT_PATH = "/".join(__file__.split("/")[:-2])

COMPLETIONS_PATH = os.path.join(CURRENT_PATH, ".complete") 
HISTORY_PATH = os.path.join(CURRENT_PATH, ".history") 

###### START READLINE SETUP ######

completions = [world for world in COMPLETIONS_PATH]

def _rline_completer(text: str, state):
    if text:
        # TODO: optimation
        matches = [s for s in completions if s and s.startswith(text)]
    else:
        matches = completions[:]
    
    try:
        return matches[state]
    except IndexError:
        return None
    
def _rline_start():
    readline.read_history_file(HISTORY_PATH)
    readline.set_completer(_rline_completer)
    readline.parse_and_bind("tab: complete")

###### FINISH READLINE SETUP ######

_reset_ansi = "\033[38;5;0m"

def clear():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

def table(headers: list, rows: list, style_c="-", spaced = 2):
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
        print("\t".join("{0:{1}}".format(header, max_widths[i]) for i, header in enumerate(headers)))
        print("\t".join(style_c * width for width in max_widths))

        # Priting rows
        for row in rows:
            print("\t".join("{0:{1}}".format(cell, max_widths[i]) for i, cell in enumerate(row)))
    else:
        # Priting headers and separators
        print((" " * spaced) + ("\t".join("{0:{1}}".format(header, max_widths[i]) for i, header in enumerate(headers))))
        print((" " * spaced) + ("\t".join(style_c * width for width in max_widths)))

        for row in rows:
            # Priting rows
            print((" " * spaced) + ("\t".join("{0:{1}}".format(cell, max_widths[i]) for i, cell in enumerate(row))))

    print()

def ansi_color(code: int) -> str:
    return f"\033[38;5;{code}m"

def banner():
    pass

def input_args(prompt: str) -> list[str]:
    getted = input(prompt)

    readline.add_history(getted)
    args = getted.split()

    return args