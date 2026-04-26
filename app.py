import streamlit as st
import pandas as pd

from data.api_manager import get_odds
from model.predict import run_model


# -----------------------
# PAGE CONFIG
# -----------------------
st.set_page_config(layout="wide")
st.title("🏒 NHL Over/Under Model")


# -----------------------
# LOAD DATA FUNCTION
# -----------------------
def load_data(force=False):
    data, usage = get_odds(force_refresh=force)

    st.session_state.games = data if isinstance(data, list) else []
    st.session_state.usage = usage if isinstance(usage, dict) else {}


# Initial load
if "games" not in st.session_state:
    load_data()


# -----------------------
# SIDEBAR
# -----------------------
st.sidebar.header("Controls")

if st.sidebar.button("🔄 Refresh Data"):
    load_data(force=True)

usage = st.session_state.get("usage", {})

st.sidebar.markdown("### API Usage")
st.sidebar.write("Used:", usage.get("used", "N/A"))
st.sidebar.write("Remaining:", usage.get("remaining", "N/A"))


# -----------------------
# MAIN DATA
# -----------------------
games = st.session_state.get("games", [])

st.subheader("📅 Games")

st.write(f"Total Games: {len(games)}")


# -----------------------
# NO DATA CASE
# -----------------------
if not games:
    st.warning("No games returned from API.")
    st.stop()


# -----------------------
# RUN MODEL
# -----------------------
results = run_model(games)

if not results:
    st.warning("No projections available.")
    st.stop()


# -----------------------
# DISPLAY GAME LIST
# -----------------------
st.subheader("🧾 Matchups")

game_list = [
    f"{g.get('away_team')} @ {g.get('home_team')}"
    for g in games
]

st.write(game_list)


# -----------------------
# DISPLAY MODEL OUTPUT
# -----------------------
st.subheader("📊 Over / Under Picks")

df = pd.DataFrame(results)

# Clean ordering
cols = ["game", "line", "projection", "pick", "confidence", "edge"]
df = df[[c for c in cols if c in df.columns]]

st.dataframe(df, use_container_width=True)


# -----------------------
# SIMPLE SUMMARY
# -----------------------
st.subheader("📌 Summary")

if "pick" in df.columns:
    plays = df[df["pick"] != "NO BET"]

    if not plays.empty:
        st.success(f"{len(plays)} suggested plays")

        st.dataframe(plays, use_container_width=True)
    else:
        st.info("No strong plays right now")


# -----------------------
# DEBUG SECTION
# -----------------------
with st.expander("🔍 Debug Data"):

    st.write("Sample Game Raw:")
    st.write(games[0])

    st.write("Sample Model Output:")
    st.write(results[0])