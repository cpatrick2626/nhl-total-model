import streamlit as st
import pandas as pd

from data.fetch_odds import get_odds
from model.predict import run_model
from utils.tracker import calculate_bankroll


st.set_page_config(layout="wide")
st.title("🏒 NHL Sharp Dashboard")

# -----------------------
# REFRESH
# -----------------------
if "data" not in st.session_state:
    st.session_state.data, st.session_state.usage = get_odds()

if st.sidebar.button("🔄 Refresh"):
    st.session_state.data, st.session_state.usage = get_odds(True)

games = st.session_state.data
usage = st.session_state.usage

# -----------------------
# MODEL
# -----------------------
results = run_model(games)
df = pd.DataFrame(results)

# -----------------------
# API USAGE
# -----------------------
st.sidebar.metric("Used", usage.get("used", 0))
st.sidebar.metric("Remaining", usage.get("remaining", 0))

# -----------------------
# BANKROLL
# -----------------------
bankroll = calculate_bankroll()
st.metric("Bankroll", f"${bankroll}")

# -----------------------
# TABLE
# -----------------------
st.dataframe(df, use_container_width=True)