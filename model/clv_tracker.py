import os
import json
import time

FILE = "cache/clv_results.json"


def load_clv():
    if not os.path.exists(FILE):
        return []
    try:
        with open(FILE) as f:
            return json.load(f)
    except:
        return []


def save_clv(data):
    os.makedirs("cache", exist_ok=True)
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)


# -----------------------
# LOG BET
# -----------------------
def log_bet(game, bet, line, odds):

    data = load_clv()

    data.append({
        "game": game,
        "bet": bet,
        "line_taken": line,
        "odds_taken": odds,
        "timestamp": time.time(),
        "closing_line": None,
        "clv": None
    })

    save_clv(data)


# -----------------------
# UPDATE CLOSING LINE
# -----------------------
def update_closing_lines(games):

    data = load_clv()

    for entry in data:
        if entry["closing_line"] is not None:
            continue

        for g in games:
            game_name = f"{g.get('away_team')} vs {g.get('home_team')}"

            if game_name != entry["game"]:
                continue

            for b in g.get("bookmakers", []):
                for m in b.get("markets", []):
                    if m["key"] == "totals":
                        for o in m["outcomes"]:
                            if o["name"] in entry["bet"]:
                                entry["closing_line"] = o["point"]

    save_clv(data)


# -----------------------
# CALCULATE CLV
# -----------------------
def calculate_clv():

    data = load_clv()

    for entry in data:
        if entry["closing_line"] is None:
            continue

        entry["clv"] = entry["closing_line"] - entry["line_taken"]

    save_clv(data)

    return data