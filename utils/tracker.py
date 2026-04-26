import json
from datetime import datetime

FILE = "bet_history.json"


def load_bets():
    try:
        with open(FILE) as f:
            return json.load(f)
    except:
        return []


def save_bet(bet):
    bets = load_bets()
    bets.append(bet)

    with open(FILE, "w") as f:
        json.dump(bets, f, indent=2)


def calculate_bankroll(start=1000):
    bets = load_bets()
    bankroll = start

    for b in bets:
        bankroll += b["profit"]

    return bankroll