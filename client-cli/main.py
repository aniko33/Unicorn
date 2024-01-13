from lib import cli
from lib import commands

import sys
import getpass

from hashlib import sha256


def server_connection(host: str, username: str, password: str, ssl=False) -> bool:
    if ssl:
        commands.HTTP_SESSION.verify = False
        commands.HTTP_POINT = "https://" + host
    else:
        commands.HTTP_POINT = "http://" + host

    login_request = commands.HTTP_SESSION.post(
        commands.HTTP_POINT + "/login",
        json={
            "username": username,
            "password": password
        }
    )

    if login_request.status_code != 200:
        return False

    commands.SESSION_ID = login_request.text

    return True


def main(argc: int, argv: list[str]):
    ssl_enabled = False

    if argc < 3:
        print("Usage:", __file__.split("/")
              [-1], "<host:port> <username> [--ssl]")

        quit(1)

    elif argc > 4:
        if argv[3] != "--ssl":
            print(argv[3], "is a invalid argument")
        
        else:
            ssl_enabled = True

    host = argv[1]
    username = argv[2]
    password = getpass.getpass("Password :: ")

    if not server_connection(host, username, sha256(password.encode()).hexdigest(), ssl_enabled):
        print("Connection to server has been failed")
        quit(0)

    cli._readline_start()

    while True:
        try:
            args = cli.iinput()

            if len(args) <= 0:
                continue

            func = getattr(commands, args[0])
            func(*args[1:])

        except AttributeError:
            continue

        except (KeyboardInterrupt, EOFError):
            if len(cli.preinput()) <= 0:
                print("To quit, type: 'quit'")
            else:
                print()


if __name__ == "__main__":
    main(len(sys.argv), sys.argv)
