from flask import Blueprint, jsonify

from core.agent import agents
from .auth import reserved_api

app = Blueprint("agent", __name__)

@app.route("/get_agents")
@reserved_api
def agent_get():
    agents_row = []

    for agent in agents:
        addr = agents[agent]["connection"].addr
        agents_row.append([agent, addr])

    return jsonify(agents_row)