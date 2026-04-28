from scipy.stats import norm
from model.projection import project_total
from model.kelly import kelly


def extract_totals(game):
    bookmakers = game.get("bookmakers", [])

    for book in bookmakers:
        for market in book.get("markets", []):
            if market.get("key") == "totals":
                for o in market.get("outcomes", []):
                    if "Over" in o.get("name", ""):
                        return o.get("point")

    return None


def prob_over(line, projection):
    return 1 - norm.cdf(line, projection, 1.5)


def run_model(games):
    results = []

    for g in games:
        home = g.get("home_team")
        away = g.get("away_team")

        line = extract_totals(g)
        if not line:
            continue

        projection = project_total(home, away)
        prob = prob_over(line, projection)

        edge = round(prob - 0.5, 4)
        pick = "OVER" if prob > 0.5 else "UNDER"

        if projection >= 6.8:
            alt = "Over 5.5"
        elif projection <= 5.2:
            alt = "Under 6.5"
        else:
            alt = "Under 7.5"

        if edge > 0.07:
            confidence = "HIGH"
        elif edge > 0.04:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

        units = round(kelly(prob) * 0.25, 2)

        results.append({
            "game": f"{away} @ {home}",
            "line": line,
            "projection": projection,
            "edge": edge,
            "pick": pick,
            "alt_pick": alt,
            "confidence": confidence,
            "units": units,
            "steam": False
        })

    return results
