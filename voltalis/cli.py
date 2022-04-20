import logging
import logging.config
import os
import sys
from . import VoltalisClient

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
        modes = cli.modeList(site.uid)
        cli.schedulerList(site.uid)

        # en live
        cli.immediateConsumptionCharts(site.uid)

        # sur l'année
        cli.annualConsumptionChartsCharts(site.uid)
        cli.totalModulatedPower(site.uid)
        cli.countryConsumptionMap(site.uid)

        return

        # turn on/off modulators
        def turn_on_function(modulator: Modulator):
            return "Salon" not in modulator.name

        cli.updateOnOff(site.uid, turn_on_function=turn_on_function)

        mode = next(modes.get("programmationModeList", []), None)
        if mode:
            cli.updateModeConfig(site.uid, mode)


if __name__ == "__main__":
    username = sys.argv[1]
    password = sys.argv[2]
    main(username, password)
