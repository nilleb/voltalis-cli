import json
import urllib.parse

from enum import Enum
from typing import Optional, List

class Modulator(object):
    def __init__(self, modulator_json) -> None:
        self.document = modulator_json
        values = modulator_json.get("values", {}).get("2", {})
        self.uid = values.get("csLinkId")  # integer
        self.name = values.get("name")  # string
        self.color = values.get("color")  # hexadecimal


class Site(object):
    def __init__(self, site_json) -> None:
        self.document = site_json
        self.uid = site_json.get("id")
        modulator_list = site_json.get("modulatorList", [])
        self.modulators = [Modulator(modulator) for modulator in modulator_list]


class TokenEncoder(object):
    def __init__(self, token) -> None:
        self.token = token

    def encoded(self):
        stringified_token = json.dumps(
            self.token, separators=(",", ":"), ensure_ascii=False
        )
        encoded_token = urllib.parse.quote_plus(stringified_token)
        encoded_token = (
            encoded_token.replace("%21", "!")
            .replace("+", "%20")
            .replace("%2A", "*")
            .replace("%29", ")")
        )
        return encoded_token

    def as_cookie(self, subscriber_id):
        token_value = self.encoded()
        cookie_value = (
            f"%7B%22token%22%3A{token_value}%2C%22subscriberId%22%3A{subscriber_id}%7D"
        )
        return {"rememberMe": cookie_value}


class Token(object):
    def __init__(self, response_json) -> None:
        self.document = response_json.get("loginToken", {})
        self.value = self.document.get("value", {}).get("token", "")
        # the token lasts 2 years

    def as_cookie(self):
        value = self.document.get("value")
        token = value.get("token")
        subscriber_id = value.get("subscriberId")
        return TokenEncoder(token).as_cookie(subscriber_id)

class Group:
    id: None
    id_sensor: None
    temp: None
    programmation_mode: None

    def __init__(self, id: None, id_sensor: None, temp: None, programmation_mode: None) -> None:
        self.id = id
        self.id_sensor = id_sensor
        self.temp = temp
        self.programmation_mode = programmation_mode


class ImageName(Enum):
    COMFORT = "comfort"
    ECO = "eco"
    MARCHE = "marche"
    NO_FROST = "noFrost"
    STOP = "stop"
    TEMPERATURE = "temperature"


class TranslationKey(Enum):
    COMFORT = "comfort"
    ECO = "eco"
    NO_FROST = "no-frost"
    OFF = "off"
    ON = "on"
    TEMPERATURE = "temperature"


class CurrentProgrammationModeElement:
    order: int
    db_id: int
    image_name: ImageName
    translation_key: TranslationKey
    is_enabled: bool
    id_ref_type_modulator: int
    required_modulator_type_id: Optional[int]

    def __init__(self, order: int, db_id: int, image_name: ImageName, translation_key: TranslationKey, is_enabled: bool, id_ref_type_modulator: int, required_modulator_type_id: Optional[int]) -> None:
        self.order = order
        self.db_id = db_id
        self.image_name = image_name
        self.translation_key = translation_key
        self.is_enabled = is_enabled
        self.id_ref_type_modulator = id_ref_type_modulator
        self.required_modulator_type_id = required_modulator_type_id


class Target:
    name: str
    group_id: None
    status: bool
    id: int
    id_to_cut: int
    is_eco_v: bool
    modulator_type_id: int
    current_programmation_mode: CurrentProgrammationModeElement
    available_programmation_mode: List[CurrentProgrammationModeElement]
    setpoint_temperature_in_celsius: Optional[int]

    def __init__(self, name: str, group_id: None, status: bool, id: int, id_to_cut: int, is_eco_v: bool, modulator_type_id: int, current_programmation_mode: CurrentProgrammationModeElement, available_programmation_mode: List[CurrentProgrammationModeElement], setpoint_temperature_in_celsius: Optional[int]) -> None:
        self.name = name
        self.group_id = group_id
        self.status = status
        self.id = id
        self.id_to_cut = id_to_cut
        self.is_eco_v = is_eco_v
        self.modulator_type_id = modulator_type_id
        self.current_programmation_mode = current_programmation_mode
        self.available_programmation_mode = available_programmation_mode
        self.setpoint_temperature_in_celsius = setpoint_temperature_in_celsius


class ProgrammationMode:
    id: None
    name: str
    type: int
    color: str
    group: List[Group]
    targets: List[Target]

    def __init__(self, id: None, name: str, type: int, color: str, group: List[Group], targets: List[Target]) -> None:
        self.id = id
        self.name = name
        self.type = type
        self.color = color
        self.group = group
        self.targets = targets


class ProgrammationModeDefinition:
    programmation_mode: ProgrammationMode

    def __init__(self, programmation_mode: ProgrammationMode) -> None:
        self.programmation_mode = programmation_mode
