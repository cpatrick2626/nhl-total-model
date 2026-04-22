import streamlit as st
import pandas as pd
from data.nhl_api import get_schedule, get_team_last_games
from data.odds_api import get_nhl_odds
from model.features import build_features
from model.predictor import predict_ml
from model.ensemble import ensemble_projection
from model.alt_selector import find_best_alt_line
from model.bet_sizing import kelly_fraction
from config import WEIGHTS, THRESHOLDS, BANKROLL, KELLY_FRACTION

st.title("🏒 NHL Total Goals Model")

games = get_schedule()
odds_data = get_nhl_odds()

all_plays = []

for _, game in games.iterrows():
    home = game["home"]
    away = game["away"]

    try:
        home_df = get_team_last_games(home)
        away_df = get_team_last_games(away)

        home_stats = {
            "gf": home_df["goals_for"].mean(),
            "ga": home_df["goals_against"].mean(),
            "sf": home_df["shots_for"].mean(),
        }

        away_stats = {
            "gf": away_df["goals_for"].mean(),
            "ga": away_df["goals_against"].mean(),
            "sf": away_df["shots_for"].mean(),
        }

        game_odds = [
            o for o in odds_data
            if o["home"] == home and o["away"] == away
        ]

        if not game_odds:
            continue

        vegas_line = game_odds[0]["point"]

        features = build_features(home_stats, away_stats, vegas_line)

        ml_total = predict_ml(features)
        poisson_total = (home_stats["gf"] + away_stats["gf"]) / 2

        final_total = ensemble_projection(
            ml_total,
            poisson_total,
            vegas_line,
            WEIGHTS
        )

        # simple distribution
        dist = {i: 1/10 for i in range(10)}

        best_play = find_best_alt_line(
            dist,
            game_odds,
            final_total,
            THRESHOLDS
        )

        if best_play:
            prob = best_play["prob"]
            odds = best_play["odds"]

            kelly = kelly_fraction(prob, odds)
            bet_size = BANKROLL * kelly * KELLY_FRACTION

            all_plays.append({
                "game": f"{away}@{home}",
                "bet": f"{best_play['side']} {best_play['line']}",
                "odds": odds,
                "prob": round(prob, 2),
                "ev": round(best_play["ev"], 3),
                "bet_size": round(bet_size, 2)
            })

    except:
        continue

if all_plays:
    df = pd.DataFrame(all_plays)
    df = df.sort_values("ev", ascending=False).head(10)
    st.dataframe(df)
else:
    st.write("No plays found")