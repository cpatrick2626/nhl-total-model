import streamlit as st
import pandas as pd

from data.fetch_odds import get_odds
from model.predict import run_model

st.set_page_config(layout="wide")
st.title("🏒 NHL TOTAL MODEL")

# -----------------------
# LOAD DATA
# -----------------------
def load_data(force=False):
    data, usage = get_odds(force_refresh=force)
    st.session_state.data = data if isinstance(data, list) else []
    st.session_state.usage = usage if isinstance(usage, dict) else {}

# init
if "data" not in st.session_state:
    load_data()

# -----------------------
# SIDEBAR
# -----------------------
st.sidebar.markdown("### Controls")

if st.sidebar.button("🔄 Refresh Data"):
    load_data(force=True)

usage = st.session_state.get("usage", {})

st.sidebar.markdown("### API Usage")

used = usage.get("used", "N/A")
remaining = usage.get("remaining", "N/A")

st.sidebar.write("Used:", used)
st.sidebar.write("Remaining:", remaining)

# -----------------------
# DATA
# -----------------------
games = st.session_state.get("data", [])

st.subheader("📅 Games Pulled")

st.write(f"Total Games: {len(games)}")

# -----------------------
# HANDLE NO DATA
# -----------------------
if not games:
    st.warning("No games returned from API.")

    st.markdown("""
    Possible reasons:
    - Odds not posted yet  
    - Wrong region/market filters  
    - API delay  
    """)

    st.stop()

# -----------------------
# RUN MODEL
# -----------------------
results = run_model(games)

# -----------------------
# RAW GAME LIST (ALWAYS SHOW)
# -----------------------
game_list = [
    f"{g.get('away_team')} @ {g.get('home_team')}"
    for g in games
]

st.subheader("🧾 Game List")
st.write(game_list)

# -----------------------
# MODEL OUTPUT
# -----------------------
st.subheader("📊 Model Output")

if not results:
    st.warning("Model returned no betting results.")
    st.stop()

df = pd.DataFrame(results)

# reorder columns safely
cols = ["game", "projection", "bet", "odds", "edge"]
df = df[[c for c in cols if c in df.columns]]

st.dataframe(df, use_container_width=True)

# -----------------------
# EDGE SUMMARY
# -----------------------
st.subheader("📌 Edge Summary")

if "edge" in df.columns:
    plays = df[df["edge"] > 0.02]

    if not plays.empty:
        st.success(f"{len(plays)} playable edges found")
        st.dataframe(plays, use_container_width=True)
    else:
        st.info("No strong edges right now")
else:
    st.info("No edge data available")

# -----------------------
# DEBUG (OPTIONAL)
# -----------------------
with st.expander("🔍 Debug Info"):
    st.write("Sample Game:", games[0] if games else "None")