import streamlit as st
import pandas as pd

from data.fetch_odds import get_odds
from model.predict import run_model
from utils.tracker import calculate_bankroll

st.set_page_config(layout="wide")
st.title("🏒 NHL Sharp Dashboard")

# -----------------------
# LOAD DATA
# -----------------------
if "data" not in st.session_state:
    st.session_state.data, st.session_state.usage = get_odds()

if st.sidebar.button("🔄 Refresh"):
    st.session_state.data, st.session_state.usage = get_odds(force_refresh=True)

games = st.session_state.data
usage = st.session_state.usage

# -----------------------
# DEBUG INFO
# -----------------------
st.sidebar.markdown("### API Status")
st.sidebar.write("Used:", usage.get("used", 0))
st.sidebar.write("Remaining:", usage.get("remaining", 0))

st.write("Games pulled:", len(games))

# -----------------------
# BANKROLL
# -----------------------
bankroll = calculate_bankroll(start=100)
st.metric("Bankroll", f"${bankroll}")

# -----------------------
# RUN MODEL
# -----------------------
if not games:
    st.warning("No games returned from API.")
    st.stop()

results = run_model(games)
df = pd.DataFrame(results)

if df.empty:
    st.warning("Model returned no results.")
else:
    st.dataframe(df, use_container_width=True)