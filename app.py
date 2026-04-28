import streamlit as st
import pandas as pd

from data.api_manager import get_odds
from model.predict import run_model

st.set_page_config(layout="wide")
st.title("🏒 NHL Over / Under Model")

def load_data(force=False):
    data, usage = get_odds(force_refresh=force)

    st.session_state.games = data if isinstance(data, list) else []
    st.session_state.usage = usage if isinstance(usage, dict) else {}

if "games" not in st.session_state:
    load_data()

st.sidebar.header("Controls")

if st.sidebar.button("🔄 Refresh Data"):
    load_data(force=True)

usage = st.session_state.get("usage", {})

st.sidebar.markdown("### API Usage")
st.sidebar.write("Used:", usage.get("used", "N/A"))
st.sidebar.write("Remaining:", usage.get("remaining", "N/A"))

games = st.session_state.get("games", [])

st.subheader("📅 Games")
st.write(f"Total Games: {len(games)}")

if not games:
    st.warning("No games returned from API.")
    st.stop()

results = run_model(games)

if not results:
    st.warning("No projections available.")
    st.stop()

st.subheader("📊 Over / Under Picks")

df = pd.DataFrame(results)

if "edge" in df.columns:
    df = df.sort_values(by="edge", ascending=False)

columns_order = [
    "game",
    "line",
    "projection",
    "edge",
    "pick",
    "alt_pick",
    "confidence",
    "units",
    "steam"
]

df = df[[c for c in columns_order if c in df.columns]]

st.dataframe(df, use_container_width=True)
