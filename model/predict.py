import math
from data.splits_scraper import get_bet_splits


# -----------------------
# POISSON
# -----------------------
def poisson_pmf(k, lam):
    return (lam**k * math.exp(-lam)) / math.factorial(k)


def prob_over(lam, line):
    return sum(poisson_pmf(k, lam) for k in range(int(line) + 1, 12))


def prob_under(lam, line):
    return 1 - prob_over(lam, line)


def implied_prob(o):
    return 1 / o  # decimal odds


# -----------------------
# REAL PROJECTION (UPGRADED)
# -----------------------
def project_total(game):

    # basic team offense (goals per game)
    team_offense = {
        "Boston Bruins": 3.2,
        "Buffalo Sabres": 3.0,
        "Colorado Avalanche": 3.5,
        "Los Angeles Kings": 3.1,
        "Tampa Bay Lightning": 3.4,
        "Montréal Canadiens": 2.9,
        "Edmonton Oilers": 3.7,
        "Anaheim Ducks": 2.8,
        "Dallas Stars": 3.3,
        "Minnesota Wild": 3.1,
        "Pittsburgh Penguins": 3.2,
        "Philadelphia Flyers": 2.9,
        "Vegas Golden Knights": 3.4,
        "Utah Mammoth": 3.0
    }

    # basic team defense (goals allowed)
    team_defense = {
        "Boston Bruins": 2.9,
        "Buffalo Sabres": 3.3,
        "Colorado Avalanche": 2.8,
        "Los Angeles Kings": 3.0,
        "Tampa Bay Lightning": 3.1,
        "Montréal Canadiens": 3.4,
        "Edmonton Oilers": 3.2,
        "Anaheim Ducks": 3.6,
        "Dallas Stars": 2.9,
        "Minnesota Wild": 3.0,
        "Pittsburgh Penguins": 3.1,
        "Philadelphia Flyers": 3.3,
        "Vegas Golden Knights": 2.8,
        "Utah Mammoth": 3.2
    }

    home = game.get("home_team")
    away = game.get("away_team")

    home_off = team_offense.get(home, 3.0)
    away_off = team_offense.get(away, 3.0)

    home_def = team_defense.get(home, 3.0)
    away_def = team_defense.get(away, 3.0)

    home_goals = (home_off + away_def) / 2
    away_goals = (away_off + home_def) / 2

    return round(home_goals + away_goals, 2)


# -----------------------
# ALT TOTALS
# -----------------------
def extract_alt_lines(game):

    lines = []

    for book in game.get("bookmakers", []):
        for m in book.get("markets", []):
            if m.get("key") == "alternate_totals":

                for o in m.get("outcomes", []):
                    lines.append({
                        "book": book.get("key"),
                        "line": o.get("point"),
                        "price": o.get("price"),
                        "type": o.get("name")
                    })

    return lines


# -----------------------
# MAIN TOTALS
# -----------------------
def extract_main_totals(game):

    lines = []

    for book in game.get("bookmakers", []):
        for m in book.get("markets", []):
            if m.get("key") == "totals":

                for o in m.get("outcomes", []):
                    lines.append({
                        "book": book.get("key"),
                        "line": o.get("point"),
                        "price": o.get("price"),
                        "type": o.get("name")
                    })

    return lines


def best_prices(lines):

    best = {}

    for o in lines:
        key = (o["type"], o["line"])

        if key not in best or o["price"] > best[key]["price"]:
            best[key] = o

    return list(best.values())


# -----------------------
# MAIN MODEL
# -----------------------
def run_model(games):

    splits_data, _ = get_bet_splits()

    results = []

    for g in games:

        lam = project_total(g)

        # ALT → MAIN fallback
        lines = extract_alt_lines(g)

        if not lines:
            lines = extract_main_totals(g)

        lines = best_prices(lines)

        if not lines:
            results.append({
                "game": f"{g.get('away_team')} vs {g.get('home_team')}",
                "projection": lam,
                "bet": "NO TOTALS AVAILABLE",
                "note": "Only moneyline markets returned"
            })
            continue

        best = None

        for o in lines:

            if o["type"] == "Over":
                model_p = prob_over(lam, o["line"])
            else:
                model_p = prob_under(lam, o["line"])

            market_p = implied_prob(o["price"])

            # public sentiment (basic fallback)
            public_p = 0.5
            if splits_data:
                public_p = splits_data[0]["over_pct"] / 100

            # blended probability
            final_p = (model_p * 0.5) + (market_p * 0.3) + (public_p * 0.2)

            edge = final_p - market_p

            decision = "PASS"
            if edge > 0.05:
                decision = "STRONG"
            elif edge > 0.02:
                decision = "PLAY"

            if not best or edge > best["edge"]:
                best = {
                    "bet": f"{o['type']} {o['line']}",
                    "book": o["book"],
                    "odds": o["price"],
                    "projection": lam,
                    "edge": round(edge, 3),
                    "decision": decision
                }

        results.append({
            "game": f"{g.get('away_team')} vs {g.get('home_team')}",
            **best
        })

    return results