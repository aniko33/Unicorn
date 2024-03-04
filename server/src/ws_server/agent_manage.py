from websockets.server import WebSocketServerProtocol

from core.agent import agents
from .response import json_response

async def send_command_to_agent(websocket: WebSocketServerProtocol, cmd_exec: str, target_id: str):
    if not target_id in list(agents.keys()):
        await websocket.send(json_response("Agent not found", "error", 500))
    
    agent = agents[target_id]

    job_n = len(agent.jobs.keys()) + 1

    agent.connection.send_command(cmd_exec, job_n) 

    agent.jobs[job_n] = None

    await websocket.send(json_response({"job": job_n}, "send_command"))