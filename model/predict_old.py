from model.features import build_features
from model.simulate import simulate_total, prob_over
from model.ev import calc_ev
from model.market import extract_best_market
from model.kelly import kelly
from model.timing import timing_decision
from config import LEAGUE_AVG_SV, LEAGUE_AVG_SHOTS

def project_total(f):
    base = f["teamA_xg"] + f["teamB_xg"]
    goalie_adj = (LEAGUE_AVG_SV - f["goalie_sv"]) * 10
    pace_adj = ((f["teamA_shots"] + f["teamB_shots"] - LEAGUE_AVG_SHOTS) * 0.05)
    return base + goalie_adj + pace_adj

def run_model(games):
    results = []

    for g in games:
        market = extract_best_market(g)
        if not market:
            continue

        f = build_features(g)
        proj = project_total(f)

        sims = simulate_total(proj)
        prob = prob_over(sims, market["line"])

        ev = calc_ev(prob, market["odds"])
        k = kelly(prob, market["odds"])

        timing = timing_decision(proj, market["line"], 0)

        results.append({
            "game": g["home_team"] + " vs " + g["away_team"],
            "line": market["line"],
            "projection": proj,
            "prob": prob,
            "ev": ev,
            "bet_size": k * 1000,
            "timing": timing,
            "book": market["book"]
        })

    return sorted(results, key=lambda x: x["ev"], reverse=True)
