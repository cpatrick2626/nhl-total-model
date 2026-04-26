import math
from data.splits_scraper import get_bet_splits


def poisson_pmf(k, lam):
    return (lam**k * math.exp(-lam)) / math.factorial(k)


def prob_over(lam, line):
    return sum(poisson_pmf(k, lam) for k in range(int(line) + 1, 12))


def prob_under(lam, line):
    return 1 - prob_over(lam, line)


def implied_prob(o):
    return 1 / o  # decimal odds


def project_total():
    return 6.0


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
# MAIN TOTALS (NEW)
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

        lam = project_total()

        # 🔥 FIX: ALT → FALLBACK TO MAIN TOTALS
        lines = extract_alt_lines(g)

        if not lines:
            lines = extract_main_totals(g)

        lines = best_prices(lines)

        if not lines:
            results.append({
                "game": f"{g.get('away_team')} vs {g.get('home_team')}",
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

            public_p = 0.5
            if splits_data:
                public_p = splits_data[0]["over_pct"] / 100

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
                    "edge": round(edge, 3),
                    "decision": decision
                }

        results.append({
            "game": f"{g.get('away_team')} vs {g.get('home_team')}",
            **best
        })

    return results