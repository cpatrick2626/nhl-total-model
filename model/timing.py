def timing_decision(proj, line, move):
    edge = proj - line

    if edge > 0.5 and move <= 0:
        return "BET NOW"
    if move > 0.5:
        return "SKIP"
    return "WAIT"