import requests
import json
import time
import os

API_KEY = "YOUR_API_KEY"
CACHE_FILE = "cache/odds.json"
CACHE_TTL = 600  # 10 min


def _load_cache():
    if not os.path.exists(CACHE_FILE):
        return None

    with open(CACHE_FILE) as f:
        return json.load(f)


def _save_cache(data, usage):
    os.makedirs("cache", exist_ok=True)

    with open(CACHE_FILE, "w") as f:
        json.dump({
            "timestamp": time.time(),
            "data": data,
            "usage": usage
        }, f)


def _valid(cache):
    if not cache:
        return False
    return (time.time() - cache["timestamp"]) < CACHE_TTL


def _fetch():
    url = "https://api.the-odds-api.com/v4/sports/icehockey_nhl/odds"

    params = {
        "apiKey": API_KEY,
        "regions": "us",
        "markets": "totals,alternate_totals",
        "oddsFormat": "american"
    }

    r = requests.get(url, params=params)
    data = r.json()

    usage = {
        "used": int(r.headers.get("x-requests-used", 0)),
        "remaining": int(r.headers.get("x-requests-remaining", 0))
    }

    return data, usage


def get_odds(force_refresh=False):

    cache = _load_cache()

    if not force_refresh and _valid(cache):
        return cache["data"], cache["usage"]

    if cache and cache["usage"]["remaining"] <= 1:
        return cache["data"], cache["usage"]

    data, usage = _fetch()
    _save_cache(data, usage)

    return data, usage