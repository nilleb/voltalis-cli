import os
import logging
import logging.config
from . import VoltalisClient
import sys
from datetime import date


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
    me = cli.me()
    site_id = me.get("defaultSite", {}).get("id")
    # me['otherSites']
    quicksettings = cli.get_quicksettings(site_id)
    logging.info(
        f"{len(quicksettings)} quick settings found for site {site_id} ({me['defaultSite']['address']})"
    )
    for setting in quicksettings:
        logging.info(
            f"[{setting['enabled'] and 'x' or ' '}] {setting['name']} ({len(setting['appliancesSettings'])})"
        )
    managed_appliances = cli.get_managed_appliances(site_id)
    for managed_appliance in managed_appliances:
        logging.info(
            f"Managed appliance: {managed_appliance['name']} ({managed_appliance['applianceType']})"
        )
    cli.consumption_stats_per_hour(site_id, date(2022, 12, 31))
    cli.logout()


if __name__ == "__main__":
    username = sys.argv[1]
    password = sys.argv[2]
    main(username, password)
