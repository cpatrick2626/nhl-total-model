import requests

BASE = "https://api-web.nhle.com/v1"

def get_team_stats():
    url = f"{BASE}/standings/now"
    r = requests.get(url).json()

    teams = {}

    for t in r.get("standings", []):
        name = t["teamName"]["default"]

        gp = max(t.get("gamesPlayed", 1), 1)

        teams[name] = {
            "goals_for": t.get("goalFor", 0) / gp,
            "goals_against": t.get("goalAgainst", 0) / gp,
            "shots_for": t.get("shotsFor", 30),
            "shots_against": t.get("shotsAgainst", 30),
        }

    return teams


def pace_factor(home, away):
    avg_shots = (home["shots_for"] + away["shots_for"]) / 2
    return avg_shots / 30