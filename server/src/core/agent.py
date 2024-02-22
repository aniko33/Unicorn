class Agent:
    def __init__(self, connection: object) -> None:
        self.commands
        self.connection = connection
    
    def set_commands(self, commands: list):
        self.commands = commands

"""
agents -> dict
{
    agent_id: Agent
    
    example:
        "XYZ...": <Agent OBJ>
}
"""

agents = {}