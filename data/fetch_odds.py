import requests
from config import ODDS_API_KEY
from utils.api_manager import fetch_with_cache

URL = "https://api.the-odds-api.com/v4/sports/icehockey_nhl/odds/"


def fetch_odds_api():
    try:
        params = {
            "apiKey": ODDS_API_KEY,
            "regions": "us",
            "markets": "totals",
            "oddsFormat": "american"
        }

        res = requests.get(URL, params=params, timeout=10)

        # If request fails
        if res.status_code != 200:
            print(f"API ERROR: Status {res.status_code}")
            return []

        data = res.json()

        # If API returns error message instead of list
        if not isinstance(data, list):
            print("API RESPONSE ERROR:", data)
            return []

        cleaned_games = []

        for game in data:
            # Skip invalid games
            if "bookmakers" not in game:
                continue

            cleaned_games.append({
                "home_team": game.get("home_team"),
                "away_team": game.get("away_team"),
                "bookmakers": game.get("bookmakers", [])
            })

        return cleaned_games

    except requests.exceptions.Timeout:
        print("API TIMEOUT")
        return []

    except Exception as e:
        print("FETCH ERROR:", e)
        return []


def get_odds():
    return fetch_with_cache(
        prefix="odds",
        fetch_func=fetch_odds_api,
        max_age=300  # cache for 5 minutes
    )