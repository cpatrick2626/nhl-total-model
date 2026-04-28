def kelly(prob, odds=-110):
    if odds < 0:
        b = 100 / abs(odds)
    else:
        b = odds / 100

    return max((prob * (b + 1) - 1) / b, 0)
