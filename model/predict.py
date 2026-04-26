from utils.tracker import load_bets, calculate_bankroll
from utils.risk_engine import (
    get_risk_multiplier,
    calculate_risk_score,
    get_risk_mode,
    go_no_go_decision,
    is_max_confidence,
    max_conf_boost,
    risk_adjusted_ev
)


def extract_totals(game):

    best = None

    for book in game.get("bookmakers", []):
        for market in book.get("markets", []):
            if market.get("key") == "totals":
                for outcome in market.get("outcomes", []):
                    if outcome.get("name") == "Over":
                        if not best or outcome["price"] > best["price"]:
                            best = outcome

    if not best:
        return None

    return {
        "line": best.get("point"),
        "odds": best.get("price")
    }


def project_total():
    return 6.0


def calc_ev(prob, odds):

    if odds > 0:
        implied = 100 / (odds + 100)
    else:
        implied = abs(odds) / (abs(odds) + 100)

    return prob - implied


def score_play(ev, edge):

    score = 0

    if ev >= 0.10:
        score += 4
    elif ev >= 0.07:
        score += 3
    elif ev >= 0.05:
        score += 2

    if edge >= 1.0:
        score += 3
    elif edge >= 0.6:
        score += 2
    elif edge >= 0.4:
        score += 1

    return score


def run_model(games):

    bets = load_bets()
    bankroll = calculate_bankroll(start=100)

    parsed = []

    for g in games:

        market = extract_totals(g)
        if not market:
            continue

        line = market["line"]
        odds = market["odds"]

        projection = project_total()
        edge = projection - line

        prob = 0.5 + (edge * 0.1)
        ev = calc_ev(prob, odds)
        score = score_play(ev, abs(edge))

        parsed.append({
            "game": f"{g.get('away_team')} vs {g.get('home_team')}",
            "line": line,
            "projection": projection,
            "ev": ev,
            "score": score,
            "fd_edge": 0,
            "steam": None,
            "rlm": None
        })

    elite_count = sum(1 for g in parsed if g["score"] >= 8)
    decision = go_no_go_decision(bankroll, bets, elite_count)

    results = []

    for g in parsed:

        if decision == "NO-GO":
            continue

        risk_score = calculate_risk_score(bankroll, bets)
        risk_mode = get_risk_mode(risk_score)

        adj_ev = risk_adjusted_ev(g["ev"], risk_score)

        max_conf = is_max_confidence(
            g["score"],
            g["ev"],
            g["fd_edge"],
            g["steam"],
            g["rlm"],
            risk_mode
        )

        base = bankroll * 0.02
        bet = base * get_risk_multiplier(bets, bankroll) * max_conf_boost(max_conf)

        results.append({
            **g,
            "adj_ev": adj_ev,
            "bet_size": round(bet, 2),
            "risk_mode": risk_mode,
            "risk_score": risk_score,
            "max_conf": max_conf,
            "go_decision": decision
        })

    return results