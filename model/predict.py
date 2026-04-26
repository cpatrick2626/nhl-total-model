import numpy as np

def extract_totals(game):
    lines = []

    for book in game.get("bookmakers", []):
        for market in book.get("markets", []):
            if market.get("key") == "totals":
                for outcome in market.get("outcomes", []):
                    if "point" in outcome:
                        lines.append(outcome["point"])

    if not lines:
        return None

    return round(sum(lines) / len(lines), 2)


def get_market_spread(game):
    """Measure disagreement between books (proxy for volatility/value)"""
    lines = []

    for book in game.get("bookmakers", []):
        for market in book.get("markets", []):
            if market.get("key") == "totals":
                for outcome in market.get("outcomes", []):
                    if "point" in outcome:
                        lines.append(outcome["point"])

    if len(lines) < 2:
        return 0

    return max(lines) - min(lines)


def run_model(games):
    results = []

    for game in games:
        away = game.get("away_team")
        home = game.get("home_team")

        line = extract_totals(game)

        if line is None:
            continue

        # -----------------------
        # REALISTIC PROJECTION ENGINE
        # -----------------------

        # Base = market line (Vegas is sharp whether you like it or not)
        projection = line

        # Add randomness (simulate team variance)
        projection += np.random.normal(0, 0.35)

        # Add adjustment for line extremes
        if line <= 5.5:
            projection += 0.25   # low totals tend to go over slightly
        elif line >= 6.5:
            projection -= 0.25   # high totals slightly under

        projection = round(projection, 2)

        # -----------------------
        # EDGE CALCULATION
        # -----------------------
        edge = round(projection - line, 2)

        if edge > 0.25:
            pick = "OVER"
        elif edge < -0.25:
            pick = "UNDER"
        else:
            pick = "NO BET"

        # -----------------------
        # CONFIDENCE
        # -----------------------
        if abs(edge) > 0.75:
            confidence = "HIGH"
        elif abs(edge) > 0.4:
            confidence = "MEDIUM"
        elif abs(edge) > 0.25:
            confidence = "LOW"
        else:
            confidence = "PASS"

        # -----------------------
        # MARKET SHARPNESS (BONUS)
        # -----------------------
        spread = get_market_spread(game)

        if spread >= 1:
            steam = "🔥 Wide Market (Possible Edge)"
        else:
            steam = "Normal"

        results.append({
            "game": f"{away} vs {home}",
            "line": line,
            "projection": projection,
            "edge": edge,
            "pick": pick,
            "confidence": confidence,
            "market_spread": spread,
            "steam": steam
        })

    return results