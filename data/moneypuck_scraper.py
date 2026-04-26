import requests
import pandas as pd
from io import StringIO

URL = "https://moneypuck.com/moneypuck/playerData/teams.csv"


def get_xg_data():
    try:
        r = requests.get(URL, timeout=10)

        if r.status_code != 200:
            return {}

        df = pd.read_csv(StringIO(r.text))

        stats = {}

        for _, row in df.iterrows():
            stats[row["team"]] = {
                "xgf": row.get("xGoalsFor", 3.0),
                "xga": row.get("xGoalsAgainst", 3.0)
            }

        return stats

    except:
        return {}