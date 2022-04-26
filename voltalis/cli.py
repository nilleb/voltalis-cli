from datetime import datetime
import json
import logging
import logging.config
import os
import sys

from .types import (
    Datum,
    DayOfWeek,
    Group,
    Mode,
    ModulatorState,
    ProgrammationMode,
    Scheduler,
    TranslationKey,
    Modulator,
)
from . import ReasonedVoltalisClient, VoltalisClient


def setup_logging_from_config(config_path):
    if os.path.exists(config_path):
        logging.config.fileConfig(config_path, disable_existing_loggers=False)
    else:
        logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    return logger


setup_logging_from_config("samples/logging.ini")


def main(username, password):
    cli = VoltalisClient(username, password)
    cli.login()

    for site in cli.sites():
        # en resumé
        cli.lastMinuteConsumption(site.uid)
        cli.immediateConsumptionInkW(site.uid)
        cli.siteMaxPower(site.uid)
        modulator = site.modulators[-1]

        # on/off
        cli.onOffState(site.uid, modulator.uid)
        cli.modulatorState(site.uid, modulator.uid)

        # absence
        cli.absenceModeState(site.uid)
        cli.absenceState(site.uid, modulator.uid)

        # mon planning
        cli.availableProgrammationMode(site.uid)
        cli.modeList(site.uid)
        cli.schedulerList(site.uid)

        # en live
        cli.immediateConsumptionCharts(site.uid)

        # sur l'année
        cli.annualConsumptionChartsCharts(site.uid)
        cli.totalModulatedPower(site.uid)
        cli.countryConsumptionMap(site.uid)


def common_switch(username, password, turn_on_function):
    cli = VoltalisClient(username, password)
    cli.login()

    for site in cli.sites():
        cli.updateOnOff(site.uid, turn_on_function=turn_on_function)


def turn_all_on(username, password):
    # turn on/off modulators
    def turn_on_function(modulator: Modulator):
        return True

    common_switch(username, password, turn_on_function)


def turn_all_off(username, password):
    # turn on/off modulators
    def turn_on_function(modulator: Modulator):
        return False

    common_switch(username, password, turn_on_function)


def create_modulator_state(
    modulator: Modulator, corresponding_mode, available_modes_for_this_modulator
):
    return ModulatorState(
        modulator.name,
        None,
        status=True,
        id=modulator.uid,
        id_to_cut=modulator.uid,
        id_cs_link=None,
        id_cs_to_cut=None,
        is_eco_v=False,
        modulator_type_id=modulator.modulator_type_id,
        current_programmation_mode=corresponding_mode,
        available_programmation_mode=available_modes_for_this_modulator,
    )


def find_corresponding_mode(available_modes_for_this_modulator):
    corresponding_mode = None
    for typed_mode in available_modes_for_this_modulator:
        if typed_mode.translation_key == TranslationKey.ECO or (
            not corresponding_mode and typed_mode.translation_key == TranslationKey.ON
        ):
            corresponding_mode = typed_mode
    return corresponding_mode


def set_all_eco(username, password):
    cli = VoltalisClient(username, password)
    rcli = ReasonedVoltalisClient(cli)
    for site in cli.sites():
        targets = []
        for modulator in site.modulators:
            available_modes_for_this_modulator = rcli.get_available_modulator_modes_for(
                site.uid, modulator.modulator_type_id
            )
            corresponding_mode = find_corresponding_mode(
                available_modes_for_this_modulator
            )
            if corresponding_mode:
                logging.info(f"✅ {modulator.name}: {corresponding_mode.db_id}")
                targets.append(
                    create_modulator_state(
                        modulator,
                        corresponding_mode,
                        available_modes_for_this_modulator,
                    )
                )
            else:
                logging.warning(
                    f"⚠️ {modulator.name}: {available_modes_for_this_modulator}"
                )

        ALL_ECO_NAME = "AllEco"
        all_eco_mode = rcli.get_mode_by_name(site.uid, ALL_ECO_NAME)

        if not all_eco_mode:
            logging.info("creating a new eco mode")
            group = Group(None, None, None, None, [])
            all_eco_mode = ProgrammationMode(
                None, ALL_ECO_NAME, 0, "#f13434", [group], targets
            )
            payload = {"programmationMode": all_eco_mode.to_dict()}
            with open("dumps/request-updateModeConfig.json", "w") as fd:
                json.dump(payload, fd)

            cli.updateModeConfig(site.uid, payload)
            all_eco_mode = rcli.get_mode_by_name(site.uid, ALL_ECO_NAME)
            assert all_eco_mode

        all_eco_scheduler = rcli.get_scheduler_by_name(site.uid, ALL_ECO_NAME)

        if not all_eco_scheduler:
            now = datetime.now()
            time_begin = f"{now.hour:02d}:{now.minute+1:02d}"
            planning = [DayOfWeek(id_day=x, day_is_on=True) for x in range(1, 8)]
            scheduler_mode = Mode(
                all_eco_mode.id,
                color_mode=all_eco_mode.color,
                label_mode=all_eco_mode.name,
            )
            data = [
                Datum(time_begin="00:00", time_end=time_begin, mode=scheduler_mode),
                Datum(time_begin=time_begin, time_end="00:00", mode=scheduler_mode),
            ]
            scheduler = Scheduler(None, ALL_ECO_NAME, False, True, data, planning)
            payload = {"scheduler": scheduler.to_dict()}
            with open("dumps/request-updateSchedulerConfig.json", "w") as fd:
                json.dump(payload, fd)
            response = cli.updateSchedulerConfig(site.uid, payload)
            all_eco_scheduler_id = response.json().get('schedulerId')
        else:
            all_eco_scheduler_id = all_eco_scheduler.id

        if all_eco_scheduler_id:
            payload = {"schedulerId": all_eco_scheduler_id, "isActive": True}
            cli.changeSchedulerState(site.uid, payload)


if __name__ == "__main__":
    username = sys.argv[1]
    password = sys.argv[2]
    main(username, password)
