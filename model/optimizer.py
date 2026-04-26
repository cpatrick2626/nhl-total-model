from model.clv_tracker import calculate_clv


def adjust_model_weights():

    data = calculate_clv()

    if not data:
        return {
            "model_weight": 0.6,
            "market_weight": 0.25,
            "public_weight": 0.15
        }

    avg_clv = sum(d["clv"] for d in data if d["clv"] is not None) / max(1, len(data))

    # baseline
    model_w = 0.6
    market_w = 0.25
    public_w = 0.15

    # adjust based on performance
    if avg_clv < 0:
        model_w -= 0.05
        market_w += 0.05
    else:
        model_w += 0.05
        market_w -= 0.05

    return {
        "model_weight": round(model_w, 2),
        "market_weight": round(market_w, 2),
        "public_weight": public_w
    }