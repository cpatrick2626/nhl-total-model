import requests
from bs4 import BeautifulSoup

URL = "https://www.covers.com/sports/nhl/matchups"


def get_bet_splits():
    try:
        r = requests.get(URL, timeout=10)

        if r.status_code != 200:
            return [], "FAILED"

        soup = BeautifulSoup(r.text, "html.parser")

        rows = soup.select(".cmg_matchup_game")

        splits = []

        for row in rows:
            try:
                perc = row.select(".cmg_matchup_bet_percent")

                splits.append({
                    "over_pct": int(perc[0].text.replace("%", "")),
                    "under_pct": int(perc[1].text.replace("%", ""))
                })
            except:
                continue

        return splits, "OK"

    except:
        return [], "FAILED"