import json
import urllib.parse

from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional, List, TypeVar, Type, Callable, cast
from enum import Enum


class Modulator(object):
    def __init__(self, modulator_json) -> None:
        self.document = modulator_json
        values = modulator_json.get("values", {}).get("2", {})
        self.uid = values.get("csLinkId")  # integer
        self.name = values.get("name")  # string
        self.color = values.get("color")  # hexadecimal
        self.modulator_type_id = modulator_json.get("modulatorTypeId")


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


# generated with app.quicktype.io
T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def to_enum(c: Type[EnumT], x: Any) -> EnumT:
    assert isinstance(x, c)
    return x.value


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


@dataclass
class Group:
    id: None
    id_sensor: None
    temp: None
    programmation_mode: None
    cs_link_id_list: None

    @staticmethod
    def from_dict(obj: Any) -> "Group":
        assert isinstance(obj, dict)
        id = from_union([from_int, from_none], obj.get("id"))
        id_sensor = from_none(obj.get("idSensor"))
        temp = from_none(obj.get("temp"))
        programmation_mode = from_none(obj.get("programmationMode"))
        cs_link_id_list = from_list(
            ModulatorState.from_dict, obj.get("csLinkIdList", [])
        )
        return Group(id, id_sensor, temp, programmation_mode, cs_link_id_list)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_union([from_int, from_none], self.id)
        result["idSensor"] = from_none(self.id_sensor)
        result["temp"] = from_none(self.temp)
        result["programmationMode"] = from_none(self.programmation_mode)
        result["csLinkIdList"] = from_list(
            lambda x: to_class(ModulatorState, x),
            self.cs_link_id_list,
        )
        return result


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


@dataclass
class CurrentProgrammationModeElement:
    order: int
    db_id: int
    image_name: ImageName
    translation_key: TranslationKey
    is_enabled: bool
    id_ref_type_modulator: int
    required_modulator_type_id: Optional[int] = None

    @staticmethod
    def from_dict(obj: Any) -> "CurrentProgrammationModeElement":
        assert isinstance(obj, dict)
        order = from_int(obj.get("order"))
        db_id = from_int(obj.get("dbId"))
        image_name = ImageName(obj.get("imageName"))
        translation_key = TranslationKey(obj.get("translationKey"))
        is_enabled = from_bool(obj.get("isEnabled"))
        id_ref_type_modulator = from_int(obj.get("idRefTypeModulator"))
        required_modulator_type_id = from_union(
            [from_int, from_none], obj.get("requiredModulatorTypeId")
        )
        return CurrentProgrammationModeElement(
            order,
            db_id,
            image_name,
            translation_key,
            is_enabled,
            id_ref_type_modulator,
            required_modulator_type_id,
        )

    def to_dict(self) -> dict:
        result: dict = {}
        result["order"] = from_int(self.order)
        result["dbId"] = from_int(self.db_id)
        result["imageName"] = to_enum(ImageName, self.image_name)
        result["translationKey"] = to_enum(TranslationKey, self.translation_key)
        result["isEnabled"] = from_bool(self.is_enabled)
        result["idRefTypeModulator"] = from_int(self.id_ref_type_modulator)
        result["requiredModulatorTypeId"] = from_union(
            [from_int, from_none], self.required_modulator_type_id
        )
        return result


@dataclass
class ModulatorState:
    name: str
    group_id: None
    status: bool
    id: int
    id_to_cut: int
    id_cs_link: int
    id_cs_to_cut: int
    is_eco_v: bool
    modulator_type_id: int
    current_programmation_mode: CurrentProgrammationModeElement
    available_programmation_mode: List[CurrentProgrammationModeElement]
    setpoint_temperature_in_celsius: Optional[int] = None

    @staticmethod
    def from_dict(obj: Any) -> "ModulatorState":
        assert isinstance(obj, dict)
        name = from_union([from_none, from_str], obj.get("name"))
        group_id = from_none(obj.get("groupId"))
        status = from_union([from_none, from_bool], obj.get("status"))
        id = from_union([from_none, from_int], obj.get("id"))
        id_to_cut = from_union([from_none, from_int], obj.get("idToCut"))
        id_cs_to_cut = from_union([from_none, from_int], obj.get("idCsToCut"))
        id_cs_link = from_union([from_none, from_int], obj.get("idCsLink"))
        is_eco_v = from_union([from_none, from_bool], obj.get("isEcoV"))
        modulator_type_id = from_int(obj.get("modulatorTypeId"))
        current_programmation_mode = CurrentProgrammationModeElement.from_dict(
            obj.get("currentProgrammationMode")
        )
        available_programmation_mode = from_list(
            CurrentProgrammationModeElement.from_dict,
            obj.get(
                "availableProgrammationMode", obj.get("availableModesForModulator")
            ),
        )
        setpoint_temperature_in_celsius = from_union(
            [from_int, from_none], obj.get("setpointTemperatureInCelsius")
        )
        return ModulatorState(
            name,
            group_id,
            status,
            id,
            id_to_cut,
            id_cs_to_cut,
            id_cs_link,
            is_eco_v,
            modulator_type_id,
            current_programmation_mode,
            available_programmation_mode,
            setpoint_temperature_in_celsius,
        )

    def to_dict(self) -> dict:
        result: dict = {}
        result["name"] = from_union([from_none, from_str], self.name)
        result["groupId"] = from_none(self.group_id)
        result["status"] = from_union([from_none, from_bool], self.status)
        result["id"] = from_union([from_none, from_int], self.id)
        result["idToCut"] = from_union([from_none, from_int], self.id_to_cut)
        result["idCsToCut"] = from_union([from_none, from_int], self.id_cs_to_cut)
        result["idCsLink"] = from_union([from_none, from_int], self.id_cs_link)
        result["isEcoV"] = from_union([from_none, from_bool], self.is_eco_v)
        result["modulatorTypeId"] = from_int(self.modulator_type_id)
        result["currentProgrammationMode"] = to_class(
            CurrentProgrammationModeElement, self.current_programmation_mode
        )
        result["availableProgrammationMode"] = from_list(
            lambda x: to_class(CurrentProgrammationModeElement, x),
            self.available_programmation_mode,
        )
        result["setpointTemperatureInCelsius"] = from_union(
            [from_int, from_none], self.setpoint_temperature_in_celsius
        )
        return result


@dataclass
class ProgrammationMode:
    id: int
    name: str
    type: int
    color: str
    group: List[Group]
    targets: List[ModulatorState]

    @staticmethod
    def from_dict(obj: Any) -> "ProgrammationMode":
        assert isinstance(obj, dict)
        id = from_union([from_int, from_none], (obj.get("id")))
        name = from_str(obj.get("name"))
        type = from_union([from_none, from_int], obj.get("type"))
        color = from_str(obj.get("color"))
        group = from_list(Group.from_dict, obj.get("group"))
        targets = from_list(ModulatorState.from_dict, obj.get("targets", []))
        return ProgrammationMode(id, name, type, color, group, targets)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_union([from_none, from_int], (self.id))
        result["name"] = from_str(self.name)
        result["type"] = from_union([from_none, from_int], self.type)
        result["color"] = from_str(self.color)
        result["group"] = from_list(lambda x: to_class(Group, x), self.group)
        result["targets"] = from_list(
            lambda x: to_class(ModulatorState, x), self.targets
        )
        return result


@dataclass
class Mode:
    id: int
    color_mode: str
    label_mode: str

    @staticmethod
    def from_dict(obj: Any) -> "Mode":
        assert isinstance(obj, dict)
        id = from_int(obj.get("id"))
        color_mode = from_str(obj.get("colorMode"))
        label_mode = from_str(obj.get("labelMode"))
        return Mode(id, color_mode, label_mode)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_int(self.id)
        result["colorMode"] = from_str(self.color_mode)
        result["labelMode"] = from_str(self.label_mode)
        return result


@dataclass
class Datum:
    time_begin: str
    time_end: str
    mode: Mode

    @staticmethod
    def from_dict(obj: Any) -> "Datum":
        assert isinstance(obj, dict)
        time_begin = from_str(obj.get("timeBegin"))
        time_end = from_str(obj.get("timeEnd"))
        mode = Mode.from_dict(obj.get("mode"))
        return Datum(time_begin, time_end, mode)

    def to_dict(self) -> dict:
        result: dict = {}
        result["timeBegin"] = from_str(self.time_begin)
        result["timeEnd"] = from_str(self.time_end)
        result["mode"] = to_class(Mode, self.mode)
        return result


@dataclass
class DayOfWeek:
    id_day: int
    day_is_on: bool

    @staticmethod
    def from_dict(obj: Any) -> "DayOfWeek":
        assert isinstance(obj, dict)
        id_day = from_int(obj.get("idDay"))
        day_is_on = from_bool(obj.get("dayIsOn"))
        return DayOfWeek(id_day, day_is_on)

    def to_dict(self) -> dict:
        result: dict = {}
        result["idDay"] = from_int(self.id_day)
        result["dayIsOn"] = from_bool(self.day_is_on)
        return result


@dataclass
class Scheduler:
    id: None
    name: str
    is_active: bool
    is_exception: bool
    data: List[Datum]
    day_of_week: List[DayOfWeek]

    @staticmethod
    def from_dict(obj: Any) -> "Scheduler":
        assert isinstance(obj, dict)
        id = from_union([from_int, from_none], obj.get("id"))
        name = from_str(obj.get("name"))
        is_active = from_union([from_bool, from_int], obj.get("isActive"))
        is_exception = from_union([from_bool, from_int], obj.get("isException"))
        data = from_list(Datum.from_dict, obj.get("data"))
        day_of_week = from_list(DayOfWeek.from_dict, obj.get("dayOfWeek"))
        return Scheduler(id, name, is_active, is_exception, data, day_of_week)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = from_none(self.id)
        result["name"] = from_str(self.name)
        result["isActive"] = from_union([from_bool, from_int], self.is_active)
        result["isException"] = from_union([from_bool, from_int], self.is_exception)
        result["data"] = from_list(lambda x: to_class(Datum, x), self.data)
        result["dayOfWeek"] = from_list(
            lambda x: to_class(DayOfWeek, x), self.day_of_week
        )
        return result


if __name__ == "__main__":
    with open("private/updateModeConfig.json") as fd:
        payload = json.load(fd)
    pm = ProgrammationMode.from_dict(payload.get("programmationMode"))
    with open("private/output.json", "w") as fp:
        json.dump(pm.to_dict(), fp)

    with open("dumps/response-getModeList.bin") as fd:
        payload = json.load(fd)
    pms = payload.get("programmationModeList", [])
    for pm in pms:
        pm = ProgrammationMode.from_dict(pm)
        with open("private/output.json", "w") as fp:
            json.dump(pm.to_dict(), fp)
