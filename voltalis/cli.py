import os
import logging
import logging.config
from . import VoltalisClient
import sys


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
    cli.me()
    cli.logout()


if __name__ == "__main__":
    username = sys.argv[1]
    password = sys.argv[2]
    main(username, password)
