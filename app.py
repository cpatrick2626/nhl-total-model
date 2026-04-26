import streamlit as st
import pandas as pd

from data.api_manager import get_odds
from model.predict import run_model

from model.clv_tracker import calculate_clv, update_closing_lines
from model.journal import load_journal
from model.executor import execute_bet


# -----------------------
# PAGE CONFIG
# -----------------------
st.set_page_config(layout="wide")
st.title("🏒 NHL TOTAL MODEL")


# -----------------------
# LOAD DATA
# -----------------------
def load_data(force=False):
    data, usage = get_odds(force_refresh=force)

    st.session_state.data = data if isinstance(data, list) else []
    st.session_state.usage = usage if isinstance(usage, dict) else {}


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

st.sidebar.write("Used:", usage.get("used", "N/A"))
st.sidebar.write("Remaining:", usage.get("remaining", "N/A"))


# -----------------------
# DATA
# -----------------------
games = st.session_state.get("data", [])

st.subheader("📅 Games Pulled")
st.write(f"Total Games: {len(games)}")


# -----------------------
# NO DATA HANDLING
# -----------------------
if not games:
    st.warning("No games returned from API.")
    st.stop()


# -----------------------
# RUN MODEL
# -----------------------
results = run_model(games)


# -----------------------
# GAME LIST
# -----------------------
st.subheader("🧾 Game List")

game_list = [
    f"{g.get('away_team')} @ {g.get('home_team')}"
    for g in games
]

st.write(game_list)


# -----------------------
# MODEL OUTPUT
# -----------------------
st.subheader("📊 Model Output")

if not results:
    st.warning("Model returned no results.")
    st.stop()

df = pd.DataFrame(results)

cols = [
    "game",
    "projection",
    "bet",
    "odds",
    "edge",
    "stake_pct",
    "confidence",
    "movement",
    "steam",
    "signal"
]

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
        st.info("No strong edges")


# -----------------------
# CLV DASHBOARD
# -----------------------
st.subheader("📈 CLV Dashboard")

try:
    update_closing_lines(games)
except:
    pass

clv_data = calculate_clv()

if clv_data:
    df_clv = pd.DataFrame(clv_data)
    st.dataframe(df_clv, use_container_width=True)

    valid = df_clv[df_clv["clv"].notna()]

    if not valid.empty:
        avg_clv = valid["clv"].mean()
        st.metric("Average CLV", round(avg_clv, 3))

        if avg_clv > 0:
            st.success("Beating market")
        else:
            st.error("Not beating market")
else:
    st.info("No CLV data yet")


# -----------------------
# BET JOURNAL
# -----------------------
st.subheader("📓 Bet Journal")

journal = load_journal()

if journal:
    st.dataframe(pd.DataFrame(journal), use_container_width=True)
else:
    st.info("No bets logged yet")


# -----------------------
# EXECUTION SIMULATOR
# -----------------------
st.subheader("⚙️ Execution Simulator")

if st.button("Run Simulation"):

    sim_results = []

    for row in df.to_dict("records"):

        if row.get("confidence") in ["PLAY", "STRONG"]:

            result = execute_bet(row)
            sim_results.append(result)

    if sim_results:
        st.write(sim_results)
    else:
        st.info("No qualifying bets to simulate")


# -----------------------
# DEBUG
# -----------------------
with st.expander("🔍 Debug Info"):
    st.write("Sample Game:", games[0] if games else "None")