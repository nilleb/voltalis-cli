import requests
import logging
from datetime import date


def call(path, method=None, json=None, headers=None):
    method = method or ("POST" if json else "GET")
    headers = headers or {}
    headers["Content-Type"] = "application/json"
    return requests.request(
        method,
        f"https://api.myvoltalis.com/{path}",
        json=json,
        headers=headers,
    )


class VoltalisClient(object):
    def __init__(self, username, password, log_response_callback=None) -> None:
        self.username = username
        self.password = password
        self.common_cookies = {}
        self.login_response = None
        self.token = None
        self.log_response_callback = log_response_callback

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

    def _log_response(self, uri: str, response: requests.Response):
        if self.log_response_callback:
            self.log_response_callback(uri, response)
        if response.status_code > 299:
            logging.warning(f"{uri} -> {response.status_code}")
        else:
            logging.info(f"{uri} -> {response.status_code}")

    def me(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = call("api/account/me", headers=headers)
        self._log_response("me", response)
        return response.json()

    def logout(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = call("auth/logout", method="DELETE", headers=headers)
        self._log_response("logout", response)

    def get_quicksettings(
        self,
        site_id: int,
    ):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = call(f"api/site/{site_id}/quicksettings", headers=headers)
        self._log_response("get_quicksettings", response)
        return response.json()

    def get_quicksetting(self, site_id: int, quicksetting_id: int):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = call(
            f"api/site/{site_id}/quicksettings/{quicksetting_id}", headers=headers
        )
        self._log_response("get_quicksetting", response)
        return response.json()

    def put_quicksetting(self, site_id: int, quicksetting_id: int, quicksetting: dict):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = call(
            f"api/site/{site_id}/quicksettings/{quicksetting_id}",
            method="PUT",
            headers=headers,
            json=quicksetting,
        )
        self._log_response("put_quicksetting", response)
        return response.json()

    def enable_quicksetting(self, site_id: int, quicksetting_id: int):
        headers = {"Authorization": f"Bearer {self.token}"}
        json = {"enabled": True}
        response = call(
            f"api/site/{site_id}/quicksettings/{quicksetting_id}/enable",
            method="PUT",
            headers=headers,
            json=json,
        )
        self._log_response("enable_quicksetting", response)
        return response.json()

    def get_managed_appliances(self, site_id: int):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = call(f"api/site/{site_id}/managed-appliance", headers=headers)
        self._log_response("get_managed_appliances", response)
        return response.json()

    def reset(self, site_id: int):
        headers = {"Authorization": f"Bearer {self.token}"}
        response = call(f"api/site/{site_id}/programming/reset", headers=headers)
        self._log_response("reset", response)

    def consumption_stats_per_hour(self, site_id: int, date: date):
        date_formatted = date.strftime("%Y-%m-%d")
        headers = {"Authorization": f"Bearer {self.token}"}

        response = call(
            f"api/site/{site_id}/consumption/week/{date_formatted}?aggregationType=BY_HOUR",
            headers=headers,
        )
        self._log_response(f"consumption_stats_per_hour-{date_formatted}", response)
        return response.json()
