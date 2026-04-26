import numpy as np

START_BANKROLL = 1000

# -----------------------------
# CORE METRICS
# -----------------------------
def calculate_volatility(bets):
    profits = [b["profit"] for b in bets if b["result"] != "pending"]
    return np.std(profits) if len(profits) > 5 else 0


def current_losing_streak(bets):
    streak = 0
    for b in reversed(bets):
        if b["result"] == "loss":
            streak += 1
        else:
            break
    return streak


def current_win_streak(bets):
    streak = 0
    for b in reversed(bets):
        if b["result"] == "win":
            streak += 1
        else:
            break
    return streak


def get_peak_bankroll(bets):
    bankroll = START_BANKROLL
    peak = bankroll

    for b in bets:
        bankroll += b["profit"]
        peak = max(peak, bankroll)

    return peak


# -----------------------------
# RISK SCORE + MODE
# -----------------------------
def calculate_risk_score(bankroll, bets):
    vol = calculate_volatility(bets)
    losing = current_losing_streak(bets)
    peak = get_peak_bankroll(bets)

    drawdown = (peak - bankroll) / peak if peak > 0 else 0

    score = 0

    if vol > 50:
        score += 3
    elif vol > 30:
        score += 2

    if losing >= 5:
        score += 3
    elif losing >= 3:
        score += 2

    if drawdown >= 0.10:
        score += 3
    elif drawdown >= 0.05:
        score += 2

    return score


def get_risk_mode(score):
    if score >= 6:
        return "DEFENSIVE"
    if score >= 3:
        return "NEUTRAL"
    return "AGGRESSIVE"


# -----------------------------
# GO / NO-GO SYSTEM
# -----------------------------
def go_no_go_decision(bankroll, bets, elite_count):
    score = calculate_risk_score(bankroll, bets)
    losing = current_losing_streak(bets)

    if score >= 7 or losing >= 6:
        return "NO-GO"

    if score >= 4 or elite_count == 0:
        return "CAUTION"

    return "GO"


# -----------------------------
# BET SIZE MULTIPLIER
# -----------------------------
def get_risk_multiplier(bets, bankroll):
    vol = calculate_volatility(bets)
    losing = current_losing_streak(bets)
    winning = current_win_streak(bets)
    peak = get_peak_bankroll(bets)

    drawdown = (peak - bankroll) / peak if peak > 0 else 0

    mult = 1

    if vol > 50:
        mult *= 0.5
    elif vol > 30:
        mult *= 0.7

    if losing >= 5:
        mult *= 0.5
    elif losing >= 3:
        mult *= 0.7

    if winning >= 5:
        mult *= 1.3
    elif winning >= 3:
        mult *= 1.15

    if drawdown >= 0.10:
        mult *= 0.5
    elif drawdown >= 0.05:
        mult *= 0.7

    return mult


# -----------------------------
# 💯 MAX CONFIDENCE SIGNAL
# -----------------------------
def is_max_confidence(score, ev, fd_edge, steam, rlm, risk_mode):
    return (
        score >= 9 and
        ev >= 0.10 and
        fd_edge is not None and abs(fd_edge) >= 0.5 and
        steam is not None and
        rlm is None and
        risk_mode == "AGGRESSIVE"
    )


def max_conf_boost(max_conf):
    return 1.5 if max_conf else 1


def risk_adjusted_ev(ev, risk_score):
    if risk_score >= 6:
        return ev * 0.5
    if risk_score >= 3:
        return ev * 0.75
    return ev