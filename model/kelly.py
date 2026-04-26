def kelly(prob, odds):
    b = 100 / abs(odds) if odds < 0 else odds / 100
    return max(0, (b * prob - (1 - prob)) / b)