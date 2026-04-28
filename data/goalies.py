def goalie_adjustment(save_pct):
    if save_pct >= 0.915:
        return 0.92
    elif save_pct <= 0.895:
        return 1.08
    return 1.0