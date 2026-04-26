import requests
from config import ODDS_API_KEY
from utils.api_manager import fetch_with_cache

def fetch_odds_api():
    try:
        url = "https://api.the-odds-api.com/v4/sports/icehockey_nhl/odds/"
        params = {
            "apiKey": ODDS_API_KEY,
            "regions": "us",
            "markets": "totals"
        }
        return requests.get(url, params=params).json()
    except:
        return []

def get_odds():
    return fetch_with_cache("odds", fetch_odds_api, 300)