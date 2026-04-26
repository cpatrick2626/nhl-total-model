import math

from utils.tracker import load_bets, calculate_bankroll


# -----------------------
# POISSON
# -----------------------
def poisson_pmf(k, lam):
    return (lam**k * math.exp(-lam)) / math.factorial(k)


def prob_over(lam, line):
    return sum(poisson_pmf(k, lam) for k in range(int(line)+1, 12))


def prob_under(lam, line):
    return 1 - prob_over(lam, line)


def implied_prob(o):
    return 100/(o+100) if o > 0 else abs(o)/(abs(o)+100)


# -----------------------
# TEAM MODEL (BASIC)
# -----------------------
def project_total():
    return 6.0


# -----------------------
# EXTRACT ALL BOOKS
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
# BEST PRICE PER LINE
# -----------------------
def best_prices(lines):

    best = {}

    for o in lines:
        key = (o["type"], o["line"])

        if key not in best or o["price"] > best[key]["price"]:
            best[key] = o

    return list(best.values())


# -----------------------
# EDGE CALC
# -----------------------
def evaluate(lam, lines):

    best = None

    for o in lines:

        prob = prob_over(lam, o["line"]) if o["type"] == "Over" else prob_under(lam, o["line"])

        ev = prob - implied_prob(o["price"])

        if not best or ev > best["ev"]:
            best = {
                "bet": f"{o['type']} {o['line']}",
                "book": o["book"],
                "odds": o["price"],
                "prob": round(prob, 3),
                "ev": round(ev, 3)
            }

    return best


# -----------------------
# MAIN
# -----------------------
def run_model(games):

    bets = load_bets()
    bankroll = calculate_bankroll()

    results = []

    for g in games:

        lam = project_total()

        lines = extract_alt_lines(g)
        lines = best_prices(lines)

        best = evaluate(lam, lines) if lines else None

        results.append({
            "game": f"{g.get('away_team')} vs {g.get('home_team')}",
            "projection": lam,
            "bet": best["bet"] if best else "PASS",
            "book": best["book"] if best else None,
            "odds": best["odds"] if best else None,
            "prob": best["prob"] if best else None,
            "ev": best["ev"] if best else None
        })

    return results