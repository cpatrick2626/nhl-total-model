def calc_ev(prob, odds):
    payout = 100 / abs(odds) if odds < 0 else odds / 100
    return (prob * payout) - (1 - prob)