from datetime import datetime, timedelta

import dateutil
import pandas as pd
import requests_cache

from . import VoltalisClient


requests_cache.install_cache("example_cache", backend="sqlite")


def get_consumption_stats_per_hour_as_dataframe(
    username: str, password: str, start: datetime, end: datetime
):
    dates = pd.date_range(start, end - timedelta(days=1), freq="d").tolist()
    cli = VoltalisClient(username, password)
    cli.login()
    me = cli.me()
    site_id = me.get("defaultSite", {}).get("id")

    cumulated_data = {"totalConsumption": 0, "consumptions": []}
    for day in dates:
        data = cli.consumption_stats_per_hour(site_id, day)
        cumulated_data["totalConsumption"] += data["totalConsumption"]
        cumulated_data["consumptions"].extend(data["consumptions"])

    conso_data = {
        "kWh": {
            dateutil.parser.parse(cons["stepTimestampInUtc"]): cons[
                "totalConsumptionInWh"
            ]
            for cons in cumulated_data.get("consumptions")
        }
    }

    conso_df = pd.DataFrame(conso_data["kWh"].items(), columns=["time", "watts"])
    conso_df.set_index("time")
    return conso_df
