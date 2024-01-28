import json

# TODO: add rest/websocket responses
def wresponse(r: str | dict, type: str, __status_code=200) -> str:
    if isinstance(r, dict):
        r.update({"status": __status_code, "type": type})
        r = json.dumps(r)
    else:
        r = json.dumps({"response": r, "type": type, "status": __status_code})

    return r
