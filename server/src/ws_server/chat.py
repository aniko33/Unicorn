from core.client import clients
from .response import json_response

chat_messages = []

async def broadcast_msg(msg: str):
    chat_messages.append(msg)
    for client in [ client for client in clients.values() if client.is_wsclient() ]:
        await client.websocket.send(json_response({"username": client.username, "color": client.color, "message": msg}, "chat"))

