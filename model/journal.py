import os
import json
import time

FILE = "cache/journal.json"


def load_journal():
    if not os.path.exists(FILE):
        return []
    with open(FILE) as f:
        return json.load(f)


def save_journal(data):
    os.makedirs("cache", exist_ok=True)
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)


def log_entry(game, bet, odds, stake_pct):

    data = load_journal()

    data.append({
        "game": game,
        "bet": bet,
        "odds": odds,
        "stake_pct": stake_pct,
        "timestamp": time.time(),
        "result": None
    })

    save_journal(data)


def update_result(index, result):

    data = load_journal()

    if 0 <= index < len(data):
        data[index]["result"] = result

    save_journal(data)