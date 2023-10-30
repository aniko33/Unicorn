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

def ansi_color(code: int) -> str:
    return f"\033[38;5;{code}m"

def banner():
    pass

def input_args(prompt: str) -> list[str]:
    getted = input(prompt)

    readline.add_history(getted)
    args = getted.split()

    return args