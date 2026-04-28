import json
from datetime import datetime

FILE = "line_history.json"

def store_line(game_id, line):
    try:
        with open(FILE, "r") as f:
            data = json.load(f)
    except:
        data = {}

    if game_id not in data:
        data[game_id] = []

    data[game_id].append({
        "time": str(datetime.now()),
        "line": line
    })

    with open(FILE, "w") as f:
        json.dump(data, f)