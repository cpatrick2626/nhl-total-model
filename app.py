import streamlit as st
import pandas as pd

from data.fetch_odds import get_odds
from model.predict import run_model
from utils.tracker import load_bets, calculate_bankroll
from utils.risk_engine import calculate_risk_score, get_risk_mode


st.set_page_config(page_title="NHL Dashboard", layout="wide")
st.title("🏒 NHL Betting Dashboard")

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.header("Controls")

if st.sidebar.button("🔄 Refresh Data"):
    st.session_state.clear()

st.sidebar.header("Filters")
min_ev = st.sidebar.slider("Min EV", 0.0, 0.15, 0.0)
min_score = st.sidebar.slider("Min Score", 0, 10, 0)

# -----------------------------
# LOAD DATA
# -----------------------------
if "data" not in st.session_state:
    st.session_state.data, st.session_state.usage = get_odds()

games = st.session_state.data
usage = st.session_state.usage

results = run_model(games)
df = pd.DataFrame(results)

if df.empty:
    st.warning("No plays available.")
    st.stop()

# -----------------------------
# API USAGE DISPLAY
# -----------------------------
st.sidebar.header("API Usage")

used = usage.get("used", 0)
remaining = usage.get("remaining", 0)
limit = used + remaining if (used + remaining) > 0 else 1

st.sidebar.metric("Used", used)
st.sidebar.metric("Remaining", remaining)
st.sidebar.progress(used / limit)

# -----------------------------
# BANKROLL
# -----------------------------
bets = load_bets()
bankroll = calculate_bankroll(start=100)

risk_score = calculate_risk_score(bankroll, bets)
risk_mode = get_risk_mode(risk_score)

st.metric("Bankroll", f"${round(bankroll,2)}")
st.metric("Risk Mode", risk_mode)

# -----------------------------
# FILTER
# -----------------------------
df = df[(df["ev"] >= min_ev) & (df["score"] >= min_score)]

# -----------------------------
# TABLE
# -----------------------------
st.dataframe(df, use_container_width=True)