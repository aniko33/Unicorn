from lib import cli

import requests

HTTP_SESSION = requests.session()
HTTP_POINT = ""
SESSION_ID = ""

def test(*args):
    print(args)

def get_agents(*args):
    r = HTTP_SESSION.get(HTTP_POINT + "/get_agents/" + SESSION_ID)

    if r.status_code != 200:
        print("Error:", r.text)
        return
    
    agents = r.json()

    if len(agents) <= 0:
        print("No agents connected")
        return

    cli.table(["ID", "Host"], r.json())