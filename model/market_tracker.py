import os
import json
import time

FILE = "cache/line_history.json"


# -----------------------
# LOAD / SAVE
# -----------------------
def load_history():
    if not os.path.exists(FILE):
        return {}
    try:
        with open(FILE) as f:
            return json.load(f)
    except:
        return {}


def save_history(data):
    os.makedirs("cache", exist_ok=True)
    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)


# -----------------------
# TRACK LINES
# -----------------------
def track_lines(games):

    history = load_history()

    for g in games:

        game_id = g.get("id", "")

        for b in g.get("bookmakers", []):
            for m in b.get("markets", []):

                if m.get("key") != "totals":
                    continue

                for o in m.get("outcomes", []):

                    if o.get("point") is None:
                        continue

                    key = f"{game_id}_{o['name']}_{o['point']}"

                    if key not in history:
                        history[key] = []

                    history[key].append({
                        "time": time.time(),
                        "price": o.get("price")
                    })

    save_history(history)
    return history


# -----------------------
# MOVEMENT
# -----------------------
def get_movement(history, key):

    if key not in history or len(history[key]) < 2:
        return 0

    start = history[key][0]["price"]
    end = history[key][-1]["price"]

    return round(end - start, 3)


# -----------------------
# CLV TRACKING
# -----------------------
def calculate_clv(open_price, close_price):

    if not open_price or not close_price:
        return 0

    return round(close_price - open_price, 3)


# -----------------------
# STEAM DETECTION
# -----------------------
def detect_steam(history, key):

    if key not in history or len(history[key]) < 3:
        return False

    recent = history[key][-3:]

    move = recent[-1]["price"] - recent[0]["price"]

    # strong fast movement
    return abs(move) > 0.15


# -----------------------
# FILTER LOGIC
# -----------------------
def steam_filter(edge, movement, steam):

    # avoid chasing steam
    if steam and movement > 0.2:
        return "AVOID_CHASING"

    # good early signal
    if edge > 0.03 and abs(movement) < 0.1:
        return "EARLY_EDGE"

    # neutral
    return "NORMAL"