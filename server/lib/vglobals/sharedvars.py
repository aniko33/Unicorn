agents: dict = {} # {agent_id: { connection: connection_obj, commands: [...] } }
clients_session = {} # {username: session_id}
clients_wsocket = []
jobs = {} # {job_id: as_success | None}
listeners = {}
listeners_threads = {}
