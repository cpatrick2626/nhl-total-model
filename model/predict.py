import math

from data.moneypuck_scraper import get_xg_data
from data.goalie_scraper import get_goalies
from data.splits_scraper import get_bet_splits
from model.market_tracker import track_lines, get_movement, detect_steam, steam_filter


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
# GOALIE ADJUSTMENT
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
# PACE
# -----------------------
def pace_adjustment(home_stats, away_stats):

    home_shots = home_stats.get("shots", 30)
    away_shots = away_stats.get("shots", 30)

    league_avg = 30

    return ((home_shots + away_shots) / 2) / league_avg


# -----------------------
# PROJECTION
# -----------------------
def project_total(game, xg_data, goalies):

    home = game.get("home_team")
    away = game.get("away_team")

    home_stats = xg_data.get(home, {})
    away_stats = xg_data.get(away, {})

    home_xgf = home_stats.get("xgf", 3.0)
    away_xgf = away_stats.get("xgf", 3.0)

    home_xga = home_stats.get("xga", 3.0)
    away_xga = away_stats.get("xga", 3.0)

    base = ((home_xgf + away_xga) + (away_xgf + home_xga)) / 2

    pace = pace_adjustment(home_stats, away_stats)

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

            if m.get("key") in ["totals", "alternate_totals"]:

                for o in m.get("outcomes", []):
                    lines.append({
                        "line": o.get("point"),
                        "price": o.get("price"),
                        "type": o.get("name")
                    })

    return lines


# -----------------------
# KELLY
# -----------------------
def kelly_fraction(p, odds, fraction=0.25):

    b = odds - 1
    k = ((p * odds) - 1) / b

    if k <= 0:
        return 0

    return k * fraction


# -----------------------
# RISK ADJUSTMENT
# -----------------------
def risk_adjustment(edge, line, has_goalie):

    risk = 1.0

    if line and line >= 6.5:
        risk *= 0.8

    if edge < 0.02:
        risk *= 0.7

    if not has_goalie:
        risk *= 0.75

    return risk


# -----------------------
# EDGE TIER
# -----------------------
def edge_tier(edge):

    if edge < 0.01:
        return "NO BET"
    elif edge < 0.03:
        return "LEAN"
    elif edge < 0.06:
        return "PLAY"
    else:
        return "STRONG"


# -----------------------
# MAIN MODEL
# -----------------------
def run_model(games):

    xg_data = get_xg_data()
    goalies = get_goalies()
    splits, _ = get_bet_splits()

    history = track_lines(games)

    results = []

    for g in games:

        lam = project_total(g, xg_data, goalies)

        lines = extract_totals(g)

        home = g.get("home_team")
        away = g.get("away_team")

        home_goalie = goalies.get(home)
        away_goalie = goalies.get(away)

        has_goalie = bool(home_goalie and away_goalie)

        if not lines:
            results.append({
                "game": f"{away} vs {home}",
                "projection": lam,
                "bet": "NO ODDS",
                "edge": 0,
                "stake_pct": 0,
                "confidence": "LOW"
            })
            continue

        best = None

        for o in lines:

            if o.get("line") is None:
                continue

            key = f"{g.get('id')}_{o['type']}_{o['line']}"

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

            kelly = kelly_fraction(final_p, o["price"])
            risk = risk_adjustment(edge, o["line"], has_goalie)
            stake = kelly * risk

            movement = get_movement(history, key)
            steam = detect_steam(history, key)
            signal = steam_filter(edge, movement, steam)

            if not best or edge > best["edge"]:
                best = {
                    "bet": f"{o['type']} {o['line']}",
                    "odds": o["price"],
                    "edge": round(edge, 4),
                    "stake_pct": round(stake * 100, 2),
                    "confidence": edge_tier(edge),
                    "movement": movement,
                    "steam": steam,
                    "signal": signal
                }

        results.append({
            "game": f"{away} vs {home}",
            "projection": lam,
            **best
        })

    return results