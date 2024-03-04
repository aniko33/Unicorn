def json_response(msg: dict | str, rtype: str, status = 200) -> dict:
    if isinstance(msg, dict):
        msg.update({"type": rtype, "status": status})
    else:
        msg = {"message": msg, "type": rtype, "status": status}

    return msg