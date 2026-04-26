import os
import json

FILE = "cache/bankroll.json"


def load_bankroll():
    if not os.path.exists(FILE):
        return {"bankroll": 100}
    with open(FILE) as f:
        return json.load(f)


def save_bankroll(data):
    with open(FILE, "w") as f:
        json.dump(data, f)


# -----------------------
# APPLY RESULT
# -----------------------
def update_bankroll(stake_pct, odds, result):

    data = load_bankroll()

    bankroll = data["bankroll"]

    stake = bankroll * (stake_pct / 100)

    if result == "win":
        bankroll += stake * (odds - 1)
    elif result == "loss":
        bankroll -= stake

    data["bankroll"] = round(bankroll, 2)

    save_bankroll(data)

    return data["bankroll"]