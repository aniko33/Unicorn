from lib import logger
from lib.vglobals.sharedvars import clients_session, clients_wsocket, jobs
from lib.response import wresponse

from websockets import server
from websockets import exceptions as wsExceptions

import asyncio
import json

tasks = set()


def get_client_from_id(client_id: str):
    return list(clients_session.keys())[list(clients_session.values()).index(client_id)]


async def wait_closed(websocket: server.WebSocketServerProtocol):
    await websocket.wait_closed()
    clients_wsocket.remove(websocket)


async def remove_client(websocket: server.WebSocketServerProtocol):
    await websocket.close()
    clients_wsocket.remove(websocket)


async def broadcast_chat(msg: str, color_code: int, username: str):
    for connection in clients_wsocket:
        await connection.send(wresponse({"username": username, "color": color_code, "message": msg}, "chat", 0))
        

async def handle_messages(websocket: server.WebSocketServerProtocol):
    async for message in websocket:
        message = message.decode()  # type: ignore
        logger.debug("Message recived: " + message)
        message = json.loads(message)

        session = message["auth"]

        if not session in clients_session.values():
            await websocket.send(wresponse("Invalid session ID", "error", 401))

        mtype = message["type"]

        match mtype:
            case "chat":
                await broadcast_chat(message["msg"],message["color"], get_client_from_id(session))

            case _:
                ...

async def whandler(websocket: server.WebSocketServerProtocol):
    clients_wsocket.append(websocket)

    task = asyncio.create_task(wait_closed(websocket))

    tasks.add(task)

    try:
        await handle_messages(websocket)

    except json.decoder.JSONDecodeError:
        await websocket.send(wresponse("invalid format, you need to JSON", "error", 405))

    except wsExceptions.ConnectionClosedError:
        ...

async def _run(ip: str, port: int):
    async with server.serve(whandler, ip, port):
        logger.debug(f"Websocket server started: {ip}:{port}")
        await asyncio.Future()

def run(ip: str, port: int):
    asyncio.run(_run(ip, port))
