from websockets import server
from websockets import exceptions as wsExceptions
import json
import asyncio

from core.client import token_exist, ClientSession
from .agent_manage import *
from .response import json_response
from .chat import *
import logger

tasks = set()

# TODO: continue refactoring

# [ Connection entry point ]
async def whandler(connection: server.WebSocketServerProtocol):
    token = await connection.recv()

    if not token_exist(token):
        # TODO: Upgrade
        await connection.send({"error": "Token don't exist", "code": 405})
        await connection.close()
        
        return

    client: ClientSession = client.get(connection)
    task = asyncio.create_task(client.ws_wait_closed())

    tasks.add(task)

    try:
        await handle_messages(connection)

    except json.decoder.JSONDecodeError:
        await connection.send(json_response({"error": "invalid format, you need to JSON"}, "error", 405))

    except wsExceptions.ConnectionClosedError:
        pass

async def handle_messages(client: ClientSession):
    async for message in client.websocket:
        message = message.decode()
        logger.debug("Message recived: " + message)
        message = json.loads(message)

        mtype = message["type"]

        match mtype:
            case "chat":
                await broadcast_msg(message["msg"])

            case "sync":
                await client.websocket.send(json_response({"messages": chat_messages}, "sync"))

            case "send_command":
                await send_command_to_agent(client.websocket, message["exec"], message["target"])