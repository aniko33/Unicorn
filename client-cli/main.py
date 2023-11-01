import sys
import inquirer
import getpass

from lib import interactive
from lib.interactive import ansi_color, _reset_ansi, clear
from lib import http

PROMPT = ansi_color(4, 4) + "Unicorn" + _reset_ansi + " > "
SELECTED_AGENT = None

http_api: http.HTTP_API = None

def server_connection() -> http.HTTP_API:
    selected_protocol = inquirer.prompt(
        [
            inquirer.List(
                "protocol",
                message="What protocol do you want to use?",
                choices=["HTTP", "HTTPS"],
            ),
        ]
    )["protocol"]

    host = input("Host (ip:port): ")
    username = input("Username: ")
    password = getpass.getpass()

    match selected_protocol:
        case "HTTP":
            http_api = http.HTTP_API(f"http://{host}", False)
        
        case "HTTPS":
            http_api = http.HTTP_API(f"https://{host}", True)

    r = http_api.login(username, password)

    if r.status_code != 200:
        print(ansi_color(9)+"ERROR: "+r.text + _reset_ansi)
        quit(1)
    else:
        http_api.session_id = r.json()["session"]

    return http_api

def main(argc: int, argv: list[str]):
    interactive._rline_start()
    
    http_api = server_connection()
    clear()

    commands = interactive.Commands(http_api)

    while True:
        try:
            cmd_arg = interactive.input_args(PROMPT)

            if len(cmd_arg) <= 0:
                continue

            exec(f"commands.{cmd_arg[0]}({cmd_arg[1:]})")

        except KeyboardInterrupt or EOFError:
            if len(interactive.preinput()) <= 0:
                print("type 'exit' to exit")
            else:
                print()

if __name__ == "__main__":
    main(len(sys.argv), sys.argv)
