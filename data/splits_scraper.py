import requests
from bs4 import BeautifulSoup
import json
import os
import time

CACHE_FILE = "cache/splits.json"
CACHE_TTL = 600

URL = "https://www.covers.com/sports/nhl/matchups"


def load_cache():
    if not os.path.exists(CACHE_FILE):
        return None

    with open(CACHE_FILE) as f:
        data = json.load(f)

    if time.time() - data["timestamp"] > CACHE_TTL:
        return None

    return data["splits"]


def save_cache(splits):
    os.makedirs("cache", exist_ok=True)

    with open(CACHE_FILE, "w") as f:
        json.dump({
            "timestamp": time.time(),
            "splits": splits
        }, f)


def validate_splits(splits):
    if not splits or len(splits) < 2:
        return False

    for s in splits:
        if "over_pct" not in s:
            return False

    return True


def fetch_splits():
    try:
        r = requests.get(URL, timeout=10)

        if r.status_code != 200:
            return None

        soup = BeautifulSoup(r.text, "html.parser")

        rows = soup.select(".cmg_matchup_list .cmg_matchup_game")

        splits = []

        for row in rows:
            try:
                teams = row.select(".cmg_matchup_team_name")
                perc = row.select(".cmg_matchup_bet_percent")

                splits.append({
                    "away": teams[0].text.strip(),
                    "home": teams[1].text.strip(),
                    "over_pct": int(perc[0].text.replace("%", "")),
                    "under_pct": int(perc[1].text.replace("%", ""))
                })
            except:
                continue

        return splits

    except:
        return None


def get_bet_splits():

    cached = load_cache()
    if cached:
        return cached, "PRIMARY"

    fresh = fetch_splits()

    if validate_splits(fresh):
        save_cache(fresh)
        return fresh, "PRIMARY"

    return [], "FAILED"