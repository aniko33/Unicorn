import requests
import hashlib
import urllib3

urllib3.disable_warnings()


class HTTP_API:
    def __init__(self, host: str, https: bool) -> None:
        self.session_id = None
        self.host = host
        self.http_client = requests.Session()

        if https:
            self.http_client.verify = False

    def login(self, username: str, password: str) -> requests.Response:
        password_hashed: str = hashlib.sha256(password.encode()).hexdigest()

        r = self.http_client.post(
            self.host + "/access",
            json={"username": username, "password": password_hashed},
        )

        return r

    def get_agents(self) -> requests.Response:
        return self.http_client.get(self.host + "/get_agents/" + self.session_id)

    def check_exist_agent(self, fingerprint: str) -> requests.Response:
        return self.http_client.post(
            self.host + "/exist_agent",
            json={"session": self.session_id, "fingerprint": fingerprint},
        )
