# model/predict.py

import random


def extract_total_line(game):
    for book in game.get("bookmakers", []):
        for market in book.get("markets", []):
            if market["key"] == "totals":
                for outcome in market["outcomes"]:
                    if outcome["name"] == "Over":
                        return outcome.get("point"), outcome.get("price")
    return None, None


def estimate_game_total(game):
    """
    VERY SIMPLE baseline model (we improve later)
    """

    # Placeholder logic (replace later with real stats)
    base = 6

    # Add slight variation so it's not dead flat
    variation = random.uniform(-0.8, 0.8)

    return round(base + variation, 2)


def run_model(games):

    results = []

    for game in games:

        line, over_price = extract_total_line(game)

        if line is None:
            continue

        projection = estimate_game_total(game)

        diff = projection - line

        # -----------------------
        # DECISION LOGIC
        # -----------------------
        if diff > 0.4:
            pick = "OVER"
            confidence = "STRONG"

        elif diff > 0.15:
            pick = "OVER"
            confidence = "LEAN"

        elif diff < -0.4:
            pick = "UNDER"
            confidence = "STRONG"

        elif diff < -0.15:
            pick = "UNDER"
            confidence = "LEAN"

        else:
            pick = "NO BET"
            confidence = "NONE"

        results.append({
            "game": f"{game['away_team']} @ {game['home_team']}",
            "line": line,
            "projection": projection,
            "pick": pick,
            "confidence": confidence,
            "edge": round(diff, 2)
        })

    return results