import streamlit as st
import pandas as pd

from data.fetch_odds import get_odds
from model.predict import run_model

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
# API STATUS
# -----------------------
st.sidebar.markdown("### API Status")
st.sidebar.write("Used:", usage.get("used", 0))
st.sidebar.write("Remaining:", usage.get("remaining", 0))

st.write("Games pulled:", len(games))

# -----------------------
# MODEL
# -----------------------
if not games:
    st.warning("No games or odds available right now.")
    st.stop()

results = run_model(games)
df = pd.DataFrame(results)

st.dataframe(df, use_container_width=True)