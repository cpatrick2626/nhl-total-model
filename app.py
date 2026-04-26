# app.py

import streamlit as st
import pandas as pd

from data.fetch_odds import get_odds
from model.predict import run_model
from utils.tracker import load_bets, calculate_bankroll
from utils.risk_engine import calculate_risk_score, get_risk_mode


# -----------------------------
# PAGE SETUP
# -----------------------------
st.set_page_config(page_title="NHL Sharp Dashboard", layout="wide")
st.title("🏒 NHL Betting Dashboard")

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data(ttl=300)
def load_data():
    games = get_odds()
    return run_model(games)

results = load_data()

if not results:
    st.warning("No plays available.")
    st.stop()

df = pd.DataFrame(results)

# -----------------------------
# BANKROLL + RISK STATUS
# -----------------------------
bets = load_bets()
bankroll = calculate_bankroll()

risk_score = calculate_risk_score(bankroll, bets)
risk_mode = get_risk_mode(risk_score)

col1, col2, col3 = st.columns(3)

col1.metric("Bankroll", f"${round(bankroll,2)}")
col2.metric("Risk Score", risk_score)
col3.metric("Mode", risk_mode)

# -----------------------------
# FILTERS
# -----------------------------
st.sidebar.header("Filters")

min_ev = st.sidebar.slider("Min EV", 0.0, 0.15, 0.05)
min_score = st.sidebar.slider("Min Score", 0, 10, 4)
elite_only = st.sidebar.checkbox("🔥 Elite Only", True)

df = df[(df["ev"] >= min_ev) & (df["score"] >= min_score)]

if elite_only:
    df = df[(df["score"] >= 8) | (df["fd_edge"].abs() >= 0.5)]

# -----------------------------
# SORT
# -----------------------------
df = df.sort_values(by="score", ascending=False)

# -----------------------------
# DISPLAY TABLE
# -----------------------------
st.markdown("## 📊 Top Plays")

display_cols = [
    "game",
    "line",
    "projection",
    "ev",
    "adj_ev",
    "score",
    "fd_edge",
    "bet_size",
    "risk_mode",
    "max_conf"
]

df_display = df[display_cols].copy()

df_display.columns = [
    "Game",
    "Line",
    "Proj",
    "EV",
    "Adj EV",
    "Score",
    "FD Edge",
    "Bet Size",
    "Mode",
    "💯"
]

# -----------------------------
# STYLE
# -----------------------------
def highlight(row):
    if row["💯"]:
        return ["background-color: gold"] * len(row)
    return [""] * len(row)

styled = df_display.style.apply(highlight, axis=1)

st.dataframe(styled, use_container_width=True)

# -----------------------------
# FANDUEL LINKS
# -----------------------------
st.markdown("## 🎯 Quick Bet Links")

def fd_link(game):
    return f"https://sportsbook.fanduel.com/search?query={game.replace(' vs ', ' @ ')}"

for _, r in df.head(5).iterrows():
    c1, c2 = st.columns([3,1])

    with c1:
        label = "💯" if r["max_conf"] else ""
        st.write(f"{label} {r['game']} → ${r['bet_size']}")

    with c2:
        st.link_button("Open", fd_link(r["game"]))

# -----------------------------
# 💯 SIGNAL PERFORMANCE
# -----------------------------
st.markdown("## 📊 Performance")

df_bets = pd.DataFrame(bets)

if not df_bets.empty:

    hundred = df_bets[df_bets["max_conf"] == True]

    if not hundred.empty:
        profit = hundred["profit"].sum()
        staked = hundred["stake"].sum()

        roi_100 = profit / staked if staked > 0 else 0

        st.metric("💯 ROI", f"{round(roi_100*100,2)}%")

    st.write("Profit by Risk Mode")
    st.write(df_bets.groupby("risk_mode")["profit"].sum())

else:
    st.info("No bet history yet.")