import math

from data.moneypuck_scraper import get_xg_data
from data.goalie_scraper import get_goalies
from data.splits_scraper import get_bet_splits


# -----------------------
# POISSON
# -----------------------
def poisson(k, lam):
    return (lam**k * math.exp(-lam)) / math.factorial(k)


def prob_over(lam, line):
    return sum(poisson(k, lam) for k in range(int(line) + 1, 12))


def implied_prob(o):
    return 1 / o


# -----------------------
# GOALIE MODEL
# -----------------------
def goalie_adjustment(name):

    if not name:
        return 0

    name = name.lower()

    elite = ["shester", "helle", "vasilev", "saros"]
    bad = ["rookie", "backup"]

    if any(x in name for x in elite):
        return -0.4

    if any(x in name for x in bad):
        return +0.5

    return 0


# -----------------------
# PACE MODEL (NEW)
# -----------------------
def pace_adjustment(home_stats, away_stats):

    home_shots = home_stats.get("shots", 30)
    away_shots = away_stats.get("shots", 30)

    league_avg = 30

    pace = ((home_shots + away_shots) / 2) / league_avg

    return pace


# -----------------------
# PROJECTION ENGINE
# -----------------------
def project_total(game, xg_data, goalies):

    home = game.get("home_team")
    away = game.get("away_team")

    home_stats = xg_data.get(home, {})
    away_stats = xg_data.get(away, {})

    # xG inputs
    home_xgf = home_stats.get("xgf", 3.0)
    away_xgf = away_stats.get("xgf", 3.0)

    home_xga = home_stats.get("xga", 3.0)
    away_xga = away_stats.get("xga", 3.0)

    # base projection
    base = ((home_xgf + away_xga) + (away_xgf + home_xga)) / 2

    # pace
    pace = pace_adjustment(home_stats, away_stats)

    # goalie impact
    home_goalie = goalies.get(home, "")
    away_goalie = goalies.get(away, "")

    goalie_adj = (
        goalie_adjustment(home_goalie) +
        goalie_adjustment(away_goalie)
    )

    lam = base * pace + goalie_adj

    return round(lam, 2)


# -----------------------
# TOTALS EXTRACTION
# -----------------------
def extract_totals(game):

    lines = []

    for b in game.get("bookmakers", []):
        for m in b.get("markets", []):

            if m["key"] in ["totals", "alternate_totals"]:

                for o in m["outcomes"]:
                    lines.append({
                        "line": o.get("point"),
                        "price": o.get("price"),
                        "type": o.get("name")
                    })

    return lines


# -----------------------
# MAIN MODEL
# -----------------------
def run_model(games):

    xg_data = get_xg_data()
    goalies = get_goalies()
    splits, _ = get_bet_splits()

    results = []

    for g in games:

        lam = project_total(g, xg_data, goalies)

        lines = extract_totals(g)

        # no odds → still show projection
        if not lines:
            results.append({
                "game": f"{g.get('away_team')} vs {g.get('home_team')}",
                "projection": lam,
                "bet": "NO ODDS",
                "edge": 0
            })
            continue

        best = None

        for o in lines:

            if o["type"] == "Over":
                model_p = prob_over(lam, o["line"])
            else:
                model_p = 1 - prob_over(lam, o["line"])

            market_p = implied_prob(o["price"])

            public_p = splits[0]["over_pct"] / 100 if splits else 0.5

            final_p = (
                model_p * 0.5 +
                market_p * 0.3 +
                public_p * 0.2
            )

            edge = final_p - market_p

            if not best or edge > best["edge"]:
                best = {
                    "bet": f"{o['type']} {o['line']}",
                    "odds": o["price"],
                    "edge": round(edge, 3)
                }

        results.append({
            "game": f"{g.get('away_team')} vs {g.get('home_team')}",
            "projection": lam,
            **best
        })

    return results