import requests
import json
import time
import os

# -----------------------
# API KEY (SAFE LOAD)
# -----------------------
try:
    import streamlit as st
    API_KEY = st.secrets.get("ODDS_API_KEY", "")
except:
    API_KEY = os.getenv("ODDS_API_KEY", "")

# -----------------------
# CACHE CONFIG
# -----------------------
CACHE_FILE = "cache/odds.json"
CACHE_TTL = 600  # seconds


# -----------------------
# CACHE HELPERS
# -----------------------
def load_cache():
    if not os.path.exists(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE) as f:
            return json.load(f)
    except:
        return None


def save_cache(data, usage):
    os.makedirs("cache", exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump({
            "timestamp": time.time(),
            "data": data,
            "usage": usage
        }, f)


def is_cache_valid(cache):
    if not cache:
        return False
    return (time.time() - cache.get("timestamp", 0)) < CACHE_TTL


# -----------------------
# USAGE PARSER (FIXED)
# -----------------------
def parse_usage(headers):
    used = headers.get("x-requests-used")
    remaining = headers.get("x-requests-remaining")

    if used is None or remaining is None:
        return {
            "used": "N/A",
            "remaining": "N/A"
        }

    try:
        return {
            "used": int(used),
            "remaining": int(remaining)
        }
    except:
        return {
            "used": "N/A",
            "remaining": "N/A"
        }


# -----------------------
# FETCH ODDS
# -----------------------
def fetch_odds():

    url = "https://api.the-odds-api.com/v4/sports/icehockey_nhl/odds"

    params = {
        "apiKey": API_KEY,
        "regions": "us,eu",  # 🔥 more coverage
        "markets": "h2h,totals",  # 🔥 avoid over-filtering
        "oddsFormat": "decimal"
    }

    try:
        r = requests.get(url, params=params, timeout=10)

        # DEBUG (safe)
        # print("STATUS:", r.status_code)
        # print("HEADERS:", dict(r.headers))

        if r.status_code != 200:
            return [], {"used": "N/A", "remaining": "N/A"}

        data = r.json()

        usage = parse_usage(r.headers)

        return data, usage

    except Exception as e:
        # print("FETCH ERROR:", e)
        return [], {"used": "N/A", "remaining": "N/A"}


# -----------------------
# MAIN ENTRY
# -----------------------
def get_odds(force_refresh=False):

    cache = load_cache()

    if not force_refresh and is_cache_valid(cache):
        return cache.get("data", []), cache.get("usage", {})

    data, usage = fetch_odds()

    # ensure safe types
    if not isinstance(data, list):
        data = []

    if not isinstance(usage, dict):
        usage = {"used": "N/A", "remaining": "N/A"}

    save_cache(data, usage)

    return data, usage