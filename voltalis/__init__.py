import requests
import logging


def call(path, method=None, json=None, headers=None):
    method = method or ('POST' if json else 'GET')
    headers = headers or {}
    headers["Content-Type"] = "application/json"
    return requests.request(
        method,
        f"https://api.myvoltalis.com/{path}",
        json=json,
        headers=headers,
    )


class VoltalisClient(object):
    def __init__(self, username, password) -> None:
        self.username = username
        self.password = password
        self.common_cookies = {}
        self.login_response = None
        self.token = None

    def login(self):
        data = {
            "password": self.password,
            "login": self.username,
        }
        self.login_response = call("auth/login", json=data)
        self.common_cookies = {
            cookie.name: cookie.value for cookie in self.login_response.cookies
        }
        self._log_response("login", self.login_response)
        self.token = self.login_response.json().get("token")

    @staticmethod
    def _log_response(uri: str, response: requests.Response):
        if response.status_code != 204:
            with open(f"dumps/response-{uri}.bin", "wb") as fd:
                fd.write(response.content)
            logging.info(f"{uri} -> {response.status_code}")

    def me(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = call("api/account/me", headers=headers)
        self._log_response("me", response)
        return response.json()

    def logout(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = call("auth/logout", method='DELETE', headers=headers)
        self._log_response("logout", response)
