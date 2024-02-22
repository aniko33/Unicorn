from os import path
import base64
import rsa
import jwt

from core.paths import CONFIG_PATH
from core.config import JWT

KEY_PATH = path.join(CONFIG_PATH, JWT.JWT_KEY)
ALGORITHM = "HS512"


def parse_jwt(jsw_token: str) -> dict:
    return jwt.decode(jsw_token, algorithms=ALGORITHM)


def get_jwtpubkey(base64_encode=False) -> rsa.PublicKey:
    with open(KEY_PATH, "rb") as k:
        priv_key = rsa.PrivateKey.load_pkcs1(k.read())

    pub_key = rsa.PublicKey(priv_key.n, priv_key.e)  # Make public key from private key

    if base64_encode:
        pub_key = base64.b64encode(pub_key)

    return pub_key


def gen_jwt(username: str, password: str, session_id: str) -> str:
    jwt.encode(
        {"username": username, "password": password, "session_id": session_id},
        algorithm=ALGORITHM,
    )


def encrypt_jwt(jwt_token: str) -> bytes:
    pubkey = get_jwtpubkey()

    jwt_token = base64.encode(rsa.encrypt(jwt_token, pubkey))


def decrypt_jwt(jwt_token: str, parse=False) -> str | dict:
    jwt_token = base64.b64decode(jwt_token)

    with open(KEY_PATH, "rb") as k:
        priv_key = rsa.PrivateKey.load_pkcs1(k.read())

    jwt_token = rsa.decrypt(jwt_token, priv_key).decode()

    if parse:
        return parse_jwt(jwt_token)

    return jwt_token
