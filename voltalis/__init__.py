import logging
from typing import Callable
import requests
from .types import (
    CurrentProgrammationModeElement,
    Modulator,
    Scheduler,
    Token,
    Site,
    ProgrammationMode,
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

        self.login_response = requests.post("https://classic.myvoltalis.com/login", data=data)
        self.common_cookies = {
            cookie.name: cookie.value for cookie in self.login_response.cookies
        }
        self._log_response("/login.json", self.login_response)
        self.token = Token(self.login_response.json())

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
        return self._call(uri, site_id)

    def countryConsumptionMap(self, site_id):
        uri = "https://myvoltalis.com/chart/getCountryConsumptionMap.json?isWebView=false&mapType=annual&useLegend=true"
        return self._call(uri, site_id)

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

        return self._call(uri, site_id, data)

    def updateModeConfig(self, site_id, data):
        uri = "https://myvoltalis.com/scheduler/updateModeConfig"
        return self._call(uri, site_id, data)

    def updateSchedulerConfig(self, site_id, data):
        uri = "https://myvoltalis.com/scheduler/updateSchedulerConfig"
        return self._call(uri, site_id, data)

    def changeSchedulerState(self, site_id, data):
        uri = "https://myvoltalis.com/scheduler/changeSchedulerState"
        return self._call(uri, site_id, data)


class ReasonedVoltalisClient(object):
    def __init__(self, cli: VoltalisClient) -> None:
        self.cli = cli

        if not getattr(self.cli, "login_response"):
            self.cli.login()

        self._cache = {}

    def key(self, method: Callable, args):
        return "$".join([method.__name__] + [repr(arg) for arg in args])

    # TODO https://stackoverflow.com/a/24778714
    def memoized(self, method, *args):
        key = self.key(method, args)
        response = self._cache.get(key, None)
        if not response:
            response = method(*args)
            self._cache[key] = response
        return response

    def get_mode_by_name(self, site_uid, name) -> ProgrammationMode:
        response = self.memoized(self.cli.modeList, site_uid)
        modes = response.json().get("programmationModeList", [])
        matching_mode = None
        for mode in modes:
            typed_mode = ProgrammationMode.from_dict(mode)
            if typed_mode.name == name:
                matching_mode = typed_mode
                break
        return matching_mode

    def get_scheduler_by_name(self, site_uid, name) -> ProgrammationMode:
        response = self.memoized(self.cli.schedulerList, site_uid)
        schedulers = response.json().get("schedulerList", [])
        matching_scheduler = None
        for scheduler in schedulers:
            typed_scheduler = Scheduler.from_dict(scheduler)
            if typed_scheduler.name == name:
                matching_scheduler = typed_scheduler
                break
        return matching_scheduler

    def get_available_modulator_modes_for(self, site_uid, modulator_type_id):
        response = self.memoized(self.cli.availableProgrammationMode, site_uid)
        available_modes = response.json().get("availableModesByModulatorType")
        available_modes_for_this_modulator = available_modes.get(
            str(modulator_type_id), []
        )
        available_modes_for_this_modulator = [
            CurrentProgrammationModeElement.from_dict(mode)
            for mode in available_modes_for_this_modulator
        ]
        return available_modes_for_this_modulator
