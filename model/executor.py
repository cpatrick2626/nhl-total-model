from model.bankroll import update_bankroll


def execute_bet(bet):

    # simulate result for now
    import random

    outcome = random.choice(["win", "loss"])

    new_bankroll = update_bankroll(
        bet["stake_pct"],
        bet["odds"],
        outcome
    )

    return {
        "result": outcome,
        "bankroll": new_bankroll
    }