import logger

from websockets import server

import json

# TODO: continue refactoring

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