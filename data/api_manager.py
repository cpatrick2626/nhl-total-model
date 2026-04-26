import requests
import json
import time
import os

API_KEY = "e5c1ba4c3752d7fec9907b519034a574"

CACHE_FILE = "cache/odds.json"
CACHE_TTL = 600


def load_cache():
    if not os.path.exists(CACHE_FILE):
        return None
    with open(CACHE_FILE) as f:
        return json.load(f)


def save_cache(data, usage):
    os.makedirs("cache", exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump({
            "timestamp": time.time(),
            "data": data,
            "usage": usage
        }, f)


def valid(cache):
    if not cache:
        return False
    return (time.time() - cache["timestamp"]) < CACHE_TTL


def fetch():

    url = "https://api.the-odds-api.com/v4/sports/icehockey_nhl/odds"

    params = {
        "apiKey": API_KEY,
        "regions": "us",
        "markets": "h2h,totals,alternate_totals",
        "oddsFormat": "decimal"
    }

    try:
        r = requests.get(url, params=params)

        if r.status_code != 200:
            return [], {"used": 0, "remaining": 0}

        data = r.json()

        usage = {
            "used": int(r.headers.get("x-requests-used", 0)),
            "remaining": int(r.headers.get("x-requests-remaining", 0))
        }

        return data, usage

    except:
        return [], {"used": 0, "remaining": 0}


def get_odds(force_refresh=False):

    cache = load_cache()

    if not force_refresh and valid(cache):
        return cache["data"], cache["usage"]

    data, usage = fetch()
    save_cache(data, usage)

    return data, usage