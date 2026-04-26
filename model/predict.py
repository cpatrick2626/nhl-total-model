import math

from data.moneypuck_scraper import get_xg_data
from data.goalie_scraper import get_goalies
from data.splits_scraper import get_bet_splits


def poisson(k, lam):
    return (lam**k * math.exp(-lam)) / math.factorial(k)


def prob_over(lam, line):
    return sum(poisson(k, lam) for k in range(int(line)+1, 12))


def implied_prob(o):
    return 1 / o


def goalie_adj(name):
    if not name:
        return 0

    if any(x in name for x in ["Vasilev", "Shester", "Helle"]):
        return -0.4

    return 0


def project_total(game, xg, goalies):

    home = game["home_team"]
    away = game["away_team"]

    home_xgf = xg.get(home, {}).get("xgf", 3.0)
    away_xgf = xg.get(away, {}).get("xgf", 3.0)

    home_xga = xg.get(home, {}).get("xga", 3.0)
    away_xga = xg.get(away, {}).get("xga", 3.0)

    base = ((home_xgf + away_xga) + (away_xgf + home_xga)) / 2

    adj = goalie_adj(goalies.get(home)) + goalie_adj(goalies.get(away))

    return round(base + adj, 2)


def extract_totals(game):

    lines = []

    for b in game.get("bookmakers", []):
        for m in b.get("markets", []):
            if m["key"] in ["totals", "alternate_totals"]:
                for o in m["outcomes"]:
                    lines.append({
                        "line": o["point"],
                        "price": o["price"],
                        "type": o["name"]
                    })

    return lines


def run_model(games):

    xg = get_xg_data()
    goalies = get_goalies()
    splits, _ = get_bet_splits()

    results = []

    for g in games:

        lam = project_total(g, xg, goalies)

        lines = extract_totals(g)

        if not lines:
            results.append({
                "game": f"{g['away_team']} vs {g['home_team']}",
                "projection": lam,
                "bet": "NO TOTALS"
            })
            continue

        best = None

        for o in lines:

            if o["type"] == "Over":
                model_p = prob_over(lam, o["line"])
            else:
                model_p = 1 - prob_over(lam, o["line"])

            market_p = implied_prob(o["price"])

            public_p = splits[0]["over_pct"]/100 if splits else 0.5

            final_p = (model_p*0.5 + market_p*0.3 + public_p*0.2)

            edge = final_p - market_p

            if not best or edge > best["edge"]:
                best = {
                    "bet": f"{o['type']} {o['line']}",
                    "odds": o["price"],
                    "edge": round(edge,3)
                }

        results.append({
            "game": f"{g['away_team']} vs {g['home_team']}",
            "projection": lam,
            **best
        })

    return results