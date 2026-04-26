import math

from utils.tracker import load_bets, calculate_bankroll
from data.splits_scraper import get_bet_splits


# -----------------------
# POISSON MODEL
# -----------------------
def poisson_pmf(k, lam):
    return (lam**k * math.exp(-lam)) / math.factorial(k)


def prob_over(lam, line):
    return sum(poisson_pmf(k, lam) for k in range(int(line) + 1, 12))


def prob_under(lam, line):
    return 1 - prob_over(lam, line)


def implied_prob(o):
    return 100/(o+100) if o > 0 else abs(o)/(abs(o)+100)


# -----------------------
# PROJECTION (TEMP - STILL WEAK)
# -----------------------
def project_total():
    return 6.0


# -----------------------
# ALT LINES (ALL BOOKS)
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


def best_prices(lines):

    best = {}

    for o in lines:
        key = (o["type"], o["line"])

        if key not in best or o["price"] > best[key]["price"]:
            best[key] = o

    return list(best.values())


# -----------------------
# DYNAMIC WEIGHTS
# -----------------------
def get_dynamic_weights(model_p, market_p, public_p):

    edge = abs(model_p - market_p)

    model_w = 0.5
    market_w = 0.3
    public_w = 0.2

    if edge > 0.05:
        model_w += 0.15
        market_w -= 0.1

    elif edge < 0.02:
        market_w += 0.1
        model_w -= 0.1

    if public_p and (public_p > 0.7 or public_p < 0.3):
        public_w -= 0.1

    return model_w, market_w, public_w


# -----------------------
# CONFIDENCE
# -----------------------
def get_confidence(edge, disagreement):

    score = 0

    if edge > 0.05:
        score += 2
    elif edge > 0.02:
        score += 1

    if disagreement < 10:
        score += 1
    elif disagreement > 20:
        score -= 1

    return score


# -----------------------
# CLASSIFICATION
# -----------------------
def classify_play(edge, confidence):

    if edge < 0.01:
        return "PASS"

    if edge > 0.05 and confidence >= 2:
        return "STRONG PLAY"

    if edge > 0.02:
        return "PLAY"

    return "PASS"


# -----------------------
# BLENDING
# -----------------------
def blend_percentages(sources):

    total_weight = 0
    weighted_sum = 0

    for s in sources:
        weighted_sum += s["over_pct"] * s["weight"]
        total_weight += s["weight"]

    return weighted_sum / total_weight if total_weight else None


def source_disagreement(sources):

    values = [s["over_pct"] for s in sources]
    return max(values) - min(values) if values else 0


# -----------------------
# MAIN MODEL
# -----------------------
def run_model(games):

    bets = load_bets()
    bankroll = calculate_bankroll(start=100)

    splits_data, source_status = get_bet_splits()

    results = []

    for g in games:

        lam = project_total()

        lines = extract_alt_lines(g)
        lines = best_prices(lines)

        if not lines:
            results.append({
                "game": f"{g.get('away_team')} vs {g.get('home_team')}",
                "bet": "NO ODDS",
                "confidence": "N/A"
            })
            continue

        best = None

        for o in lines:

            if o["type"] == "Over":
                model_p = prob_over(lam, o["line"])
            else:
                model_p = prob_under(lam, o["line"])

            market_p = implied_prob(o["price"])

            # -----------------------
            # PUBLIC (BLENDED)
            # -----------------------
            public_p = 0.5

            if splits_data:
                # naive match (can improve later)
                public_p = splits_data[0]["over_pct"] / 100

            # -----------------------
            # DYNAMIC WEIGHTS
            # -----------------------
            mw, mk, pw = get_dynamic_weights(model_p, market_p, public_p)

            final_p = (model_p * mw) + (market_p * mk) + (public_p * pw)

            # public bias adjustment
            if public_p > 0.65:
                final_p -= 0.02

            edge = final_p - market_p

            disagreement = 0  # placeholder until multi-source active
            confidence = get_confidence(edge, disagreement)

            decision = classify_play(edge, confidence)

            if not best or edge > best["edge"]:
                best = {
                    "bet": f"{o['type']} {o['line']}",
                    "book": o["book"],
                    "odds": o["price"],
                    "model_p": round(model_p, 3),
                    "market_p": round(market_p, 3),
                    "final_p": round(final_p, 3),
                    "edge": round(edge, 3),
                    "confidence": confidence,
                    "decision": decision
                }

        results.append({
            "game": f"{g.get('away_team')} vs {g.get('home_team')}",
            **best
        })

    return results