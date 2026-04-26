import streamlit as st
import pandas as pd

from data.fetch_odds import get_odds
from model.predict import run_model

st.set_page_config(layout="wide")
st.title("🏒 NHL TOTAL MODEL")

# -----------------------
# LOAD DATA (SAFE INIT)
# -----------------------
if "data" not in st.session_state:
    data, usage = get_odds()
    st.session_state.data = data
    st.session_state.usage = usage

# -----------------------
# REFRESH BUTTON
# -----------------------
if st.sidebar.button("🔄 Refresh Data"):
    data, usage = get_odds(force_refresh=True)
    st.session_state.data = data
    st.session_state.usage = usage

games = st.session_state.get("data", [])
usage = st.session_state.get("usage", {})

# -----------------------
# SIDEBAR (FIXED USAGE DISPLAY)
# -----------------------
st.sidebar.markdown("### API Usage")

used = usage.get("used", "N/A")
remaining = usage.get("remaining", "N/A")

st.sidebar.write("Used:", used)
st.sidebar.write("Remaining:", remaining)

# -----------------------
# MAIN DISPLAY
# -----------------------
if not games:
    st.warning("No games available right now.")
    st.stop()

# -----------------------
# RUN MODEL
# -----------------------
results = run_model(games)

if not results:
    st.warning("Model returned no results.")
    st.stop()

df = pd.DataFrame(results)

# -----------------------
# CLEAN DISPLAY
# -----------------------
st.subheader("📊 Model Output")

# reorder if fields exist
cols = ["game", "projection", "bet", "odds", "edge"]
df = df[[c for c in cols if c in df.columns]]

st.dataframe(df, use_container_width=True)

# -----------------------
# SUMMARY (QUICK READ)
# -----------------------
st.subheader("📌 Quick Summary")

plays = df[df.get("edge", 0) > 0.02] if "edge" in df else []

if len(plays) > 0:
    st.success(f"{len(plays)} potential plays found")
else:
    st.info("No strong edges right now")