import logging
from typing import Callable
import requests
from .types import Modulator, Token, Site

class VoltalisClient(object):
    def __init__(self, username, password) -> None:
        self.username = username
        self.password = password

    def login(self):
        data = {
            "id": "",
            "alternative_email": "",
            "email": "",
            "firstname": "",
            "lastname": "",
            "login": "",
            "password": self.password,
            "phone": "",
            "country": "",
            "selectedSiteId": "",
            "username": self.username,
            "stayLoggedIn": "true",
        }

        self.login_response = requests.post("https://myvoltalis.com/login", data=data)
        self.common_cookies = {
            cookie.name: cookie.value for cookie in self.login_response.cookies
        }
        self.token = Token(self.login_response.json())
        self._log_response("/login.json", self.login_response)

    def sites(self):
        site_list = self.login_response.json().get("subscriber", {}).get("siteList", [])
        return [Site(site) for site in site_list]

    @staticmethod
    def _log_response(uri, response):
        called = uri.split("/")[-1].split(".json")[0]

        if response.status_code != 204:
            with open(f"dumps/response-{called}.bin", "wb") as fd:
                fd.write(response.content)
            logging.info(f"{called} -> {response.status_code}")

    def _call(self, uri, site_id, data=None):
        headers = {
            "User-Site-Id": str(site_id),
            "Accept": "application/json, text/plain, */*",
        }

        if data:
            headers["Content-Type"] = "application/json;charset=UTF-8"

        cookies = self.token.as_cookie()
        cookies.update(self.common_cookies)

        method = requests.post if data else requests.get

        response = method(
            uri,
            cookies=cookies,
            headers=headers,
            json=data,
        )

        self._log_response(uri, response)

        return response

    def lastMinuteConsumption(self, site_id):
        uri = "https://myvoltalis.com/siteDataRealTime/lastMinuteConsumption.json"
        return self._call(uri, site_id)

    def immediateConsumptionInkW(self, site_id):
        uri = "https://myvoltalis.com/siteData/immediateConsumptionInkW.json"
        return self._call(uri, site_id)

    def siteMaxPower(self, site_id):
        # FIXME serialize dates
        uri = "https://myvoltalis.com/siteData/getSiteMaxPower.json?endDate=1648763999999&startDate=1617228000000"
        return self._call(uri, site_id)

    def absenceModeState(self, site_id):
        uri = "https://myvoltalis.com/programmationEvent/getAbsenceModeState.json"
        return self._call(uri, site_id)

    def absenceState(self, site_id, modulator_id):
        uri = f"https://myvoltalis.com/absence/getAbsenceState.json?csLinkId={modulator_id}"
        return self._call(uri, site_id)

    def onOffState(self, site_id, modulator_id):
        uri = f"https://myvoltalis.com/programmationEvent/getOnOffState.json?csLinkId={modulator_id}"
        return self._call(uri, site_id)

    def modulatorState(self, site_id, modulator_id):
        uri = f"https://myvoltalis.com/modulator/getModulatorState.json?csLinkId={modulator_id}"
        return self._call(uri, site_id)

    def availableProgrammationMode(self, site_id):
        uri = "https://myvoltalis.com/scheduler/availableProgrammationMode.json"
        return self._call(uri, site_id)

    def modeList(self, site_id):
        uri = "https://myvoltalis.com/scheduler/getModeList.json"
        return self._call(uri, site_id)

    def schedulerList(self, site_id):
        uri = "https://myvoltalis.com/scheduler/getSchedulerList.json"
        return self._call(uri, site_id)

    def immediateConsumptionCharts(self, site_id):
        uri = "https://myvoltalis.com/chart/getImmediateConsumptionCharts.json?chartWithLegend=true&endDate=18%2F04%2F2022&isWebView=false&startDate=18%2F04%2F2022&withSubscriptionSerie=true"
        return self._call(uri, site_id)

    def annualConsumptionChartsCharts(self, site_id):
        uri = "https://myvoltalis.com/chart/getAnnualConsumptionDetailedCharts.json?isWebView=false"
        return self._call(uri, site_id)

    def totalModulatedPower(self, site_id):
        uri = "https://myvoltalis.com/siteData/getTotalModulatedPower.json?endDate=1648763999999&startDate=1617228000000"
        self._call(uri, site_id)

    def countryConsumptionMap(self, site_id):
        uri = "https://myvoltalis.com/chart/getCountryConsumptionMap.json?isWebView=false&mapType=annual&useLegend=true"
        self._call(uri, site_id)

    @staticmethod
    def _prepare_modulator_payload(modulator: Modulator, turn_on_function: Callable):
        if not turn_on_function:
            turn_on_function = lambda x: True

        return {
            "name": modulator.name,
            "csLinkId": modulator.uid,
            "csLinkToCutId": modulator.uid,
            "modulation": False,
            "status": turn_on_function(modulator),
            "isProgrammable": True,
        }

    def _prepare_update_on_off_payload(self, site_id, turn_on_function: Callable):
        modulators_payload = []
        for modulator in {site.uid: site for site in self.sites()}[site_id].modulators:
            modulators_payload.append(
                self._prepare_modulator_payload(modulator, turn_on_function)
            )
        return {"csLinkList": modulators_payload}

    def updateOnOff(self, site_id, data=None, turn_on_function=None):
        uri = "https://myvoltalis.com/programmationEvent/updateOnOffEvent"

        if not data:
            data = self._prepare_update_on_off_payload(site_id, turn_on_function)

        self._call(uri, site_id, data)

    def updateModeConfig(self, site_id, data):
        uri = "https://myvoltalis.com/scheduler/updateModeConfig"
        self._call(uri, site_id, data)