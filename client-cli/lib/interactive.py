import readline
import os

from lib import http

INPUT_ARROW = "> "
CURRENT_PATH = "/".join(__file__.split("/")[:-2])
HISTORY_PATH = os.path.join(CURRENT_PATH, ".history")

class Commands:
    def __init__(self, api: http.HTTP_API) -> None:
        self.selected_agent = None
        self.prompt_info = ""
        self.prompt = ansi_color(4, 4) + "unicorn" + _reset_ansi

        self.api: http.HTTP_API = api

    def list_agents(self, args: list[str]):
        agents = self.api.get_agents().json()
                
        if len(agents) <= 0:
            print("No agents connected")
        else:
            table(
                ["Host", "Fingerprint", "Name"],
                agents
            )
    
    def connect(self, args: list[str]):
        target_fingerprint = args[0]
        
        agent_info = self.api.check_exist_agent(target_fingerprint).json()
        
        if agent_info["exist"]:
            self.selected_agent = target_fingerprint
            self.prompt_info = "["+agent_info["addr"]+"]"
        else:
            print("this agent don't exist")

    def send_command(self, args: list[str]):
        command = " ".join(args)
        print(self.api.send_command(self.selected_agent, command).json())
        

    def exit():
        print("Bye!\n")
        quit(0)


###### START READLINE SETUP ######

commands_methods: list[str] = list(dir(Commands))

# Get methods from Commands class - exclude special methods (__init__ etc..)
completions = [cmd for cmd in commands_methods if not cmd.startswith("__")]

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

_reset_ansi = "\033[0m"


def clear():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


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


def ansi_color(code: int, style=5) -> str:
    return f"\033[38;{style};{code}m"

def banner():
    pass

def input_args(prompt: str) -> list[str]:
        getted = input(prompt)

        readline.write_history_file(HISTORY_PATH)
        args = getted.split()
    
        return args

def preinput() -> str:
    return readline.get_line_buffer()