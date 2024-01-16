from lib import logger
from lib.vglobals.sharedvars import clients_session

from websockets import server
from websockets import exceptions as wsExceptions

import asyncio
import json

connections: list[server.WebSocketServerProtocol] = []
tasks = set()


def response(r: str | dict, type: str, __status_code=200) -> str:
    if isinstance(r, dict):
        r.update({"status": __status_code, "type": type})
        r = json.dumps(r)
    else:
        r = json.dumps({"response": r, "type": type, "status": __status_code})

    return r


def get_client_from_id(client_id: str):
    return list(clients_session.keys())[list(clients_session.values()).index(client_id)]


async def wait_closed(websocket: server.WebSocketServerProtocol):
    await websocket.wait_closed()
    connections.remove(websocket)


async def remove_client(websocket: server.WebSocketServerProtocol):
    await websocket.close()
    connections.remove(websocket)


async def broadcast_chat(msg: str, username: str):
    for connection in connections:
        await connection.send(response({"username": username, "message": msg}, "chat", 0))
        

async def handle_messages(websocket: server.WebSocketServerProtocol):
    async for message in websocket:
        message = message.decode()  # type: ignore
        logger.debug("Message recived: " + message)
        message = json.loads(message)

        session = message["auth"]

        if not session in clients_session.values():
            await websocket.send(response("Invalid session ID", "error", 401))

        mtype = message["type"]

        match mtype:
            case "chat":
                await broadcast_chat(message["msg"], get_client_from_id(session))

            case _:
                ...

async def whandler(websocket: server.WebSocketServerProtocol):
    connections.append(websocket)

    task = asyncio.create_task(wait_closed(websocket))

    tasks.add(task)

    try:
        await handle_messages(websocket)

    except json.decoder.JSONDecodeError:
        await websocket.send(response("invalid format, you need to JSON", "error", 405))

    except wsExceptions.ConnectionClosedError:
        ...

async def _run(ip: str, port: int):
    async with server.serve(whandler, ip, port):
        logger.success(f"Websocket server started: {ip}:{port}")
        await asyncio.Future()

def run(ip: str, port: int):
    asyncio.run(_run(ip, port))
