from lib import logger
from lib.vglobals.sharedvars import clients_session, clients_wsocket, agents, jobs
from lib.response import wresponse

from websockets import server
from websockets import exceptions as wsExceptions

import asyncio
import json
import ssl as _ssl

tasks = set()
chat_messages: list[dict] = []

def get_client_usrname_from_id(client_id: str) -> str:
    return list(clients_session.keys())[list(clients_session.values()).index(client_id)]


async def wait_closed(websocket: server.WebSocketServerProtocol):
    await websocket.wait_closed()
    clients_wsocket.remove(websocket)


async def remove_client(websocket: server.WebSocketServerProtocol):
    await websocket.close()
    clients_wsocket.remove(websocket)


async def broadcast_chat(msg: str, color_code: int, username: str):
    chat_messages.append({"username": username, "color": color_code, "message": msg})
    for connection in clients_wsocket:
        await connection.send(wresponse({"username": username, "color": color_code, "message": msg}, "chat", 0))

async def send_command_to_agent(websocket: server.WebSocketServerProtocol, cmd_exec: str, target_id: str):
    if not target_id in list(agents.keys()):
        await websocket.send(wresponse("Agent not found", "error", 500))
    
    agent = agents[target_id]

    job_n = len(jobs.keys()) + 1

    agent.send(json.dumps({"exec": cmd_exec, "job": job_n}).encode())

    jobs[job_n] = None

    await websocket.send(wresponse({"job": job_n}, "send_command"))

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
                await broadcast_chat(message["msg"],message["color"], get_client_usrname_from_id(session))

            case "sync":
                await websocket.send(wresponse({"messages": chat_messages}, "sync"))

            case "send_command":
                await send_command_to_agent(websocket, message["exec"], message["target"])

async def whandler(websocket: server.WebSocketServerProtocol):
    clients_wsocket.append(websocket)

    task = asyncio.create_task(wait_closed(websocket))

    tasks.add(task)

    try:
        await handle_messages(websocket)

    except json.decoder.JSONDecodeError:
        await websocket.send(wresponse("invalid format, you need to JSON", "error", 405))

    except wsExceptions.ConnectionClosedError:
        pass

async def _run(ip: str, port: int, ssl=False, ssl_context=()):
    ws_ssl_context = None
    
    if ssl:
        ws_context = _ssl.SSLContext(_ssl.PROTOCOL_TLS_SERVER)
        ws_context.load_cert_chain(*ssl_context)

    async with server.serve(whandler, ip, port, ssl=ws_ssl_context):
        logger.debug(f"Websocket server started: {ip}:{port}")
        await asyncio.Future()

def run(*args):
    asyncio.run(_run(*args))
