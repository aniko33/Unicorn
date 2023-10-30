import requests
import hashlib

# TODO: finish login

class HTTP_API:
    def __init__(self, host: str, https: bool) -> None:
        self.host = host
        self.https = https
        self.http_client = requests.Session()
        self.http_client.verify = False

    def login(self, username: str, password: str) -> str:
        password_hashed: str = hashlib.sha256(password.encode()).hexdigest()
        
        self.http_client.post(self.host, json={
            "username": username,
            "password": password_hashed
        })