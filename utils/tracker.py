import json
import os

FILE = "bets.json"


def load_bets():
    if not os.path.exists(FILE):
        return []

    with open(FILE) as f:
        return json.load(f)


def save_bet(bet):
    bets = load_bets()
    bets.append(bet)

    with open(FILE, "w") as f:
        json.dump(bets, f, indent=2)


def calculate_bankroll(start=100):
    bets = load_bets()
    bankroll = start

    for b in bets:
        bankroll += b.get("profit", 0)

    return bankroll


def implied_prob(o):
    return 100/(o+100) if o > 0 else abs(o)/(abs(o)+100)


def calculate_clv(open_odds, closing_odds):
    if closing_odds is None:
        return None
    return implied_prob(open_odds) - implied_prob(closing_odds)