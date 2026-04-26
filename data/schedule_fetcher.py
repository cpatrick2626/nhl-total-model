import requests

def get_schedule():

    url = "https://api.the-odds-api.com/v4/sports/icehockey_nhl/scores"

    try:
        r = requests.get(url, timeout=10)

        if r.status_code != 200:
            return []

        data = r.json()

        games = []

        for g in data:
            games.append({
                "home_team": g.get("home_team"),
                "away_team": g.get("away_team"),
                "commence_time": g.get("commence_time"),
                "bookmakers": []  # no odds
            })

        return games

    except:
        return []