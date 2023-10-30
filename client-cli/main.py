import sys
import inquirer
import getpass

from lib import interactive
from lib import http

PROMPT = "> "

http_api: http.HTTP_API = None

def server_connection():
    selected_protocol = inquirer.prompt(
        [
            inquirer.List(
                "protocol",
                message="What protocol do you want to use?",
                choices=["HTTP", "HTTPs"],
            ),
        ]
    )["protocol"]

    host = input("Host (ip:port): ")
    username = input("Username: ")
    password = getpass.getpass()

    match selected_protocol:
        case "HTTPS":
            http_api = http.HTTP_API(f"https://{host}", True)
        case "HTTP":
            http_api = http.HTTP_API(f"http://{host}", False)

    http_api.login(username, password)

def main(argc: int, argv: list[str]):
    interactive._rline_start()

    while True:
        interactive.input_args(PROMPT)


if __name__ == "__main__":
    main(len(sys.argv), sys.argv)
