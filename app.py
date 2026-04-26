import streamlit as st
from data.fetch_odds import get_odds
from model.predict import run_model
from streamlit_autorefresh import st_autorefresh

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="NHL Sharp Model",
    layout="wide"
)

st.title("🏒 NHL SHARP MODEL")

# -----------------------------
# AUTO REFRESH (every 30s)
# -----------------------------
st_autorefresh(interval=30000, key="refresh")

# -----------------------------
# LOAD DATA (CACHED)
# -----------------------------
@st.cache_data(ttl=300)
def load_data():
    odds = get_odds()
    results = run_model(odds)
    return odds, results

odds, results = load_data()

# -----------------------------
# DEBUG SECTION (TEMP)
# -----------------------------
with st.expander("🔍 Debug Info"):
    st.write("RAW ODDS:", odds)
    st.write("MODEL RESULTS:", results)

# -----------------------------
# DISPLAY RESULTS
# -----------------------------
st.markdown("## 🔥 TOP PLAYS")

if not results:
    st.warning("No plays found. Check API or model filtering.")
else:
    for r in results[:10]:
        st.markdown(f"""
        ### {r['game']}
        Line: {r['line']}  
        Model: {round(r['projection'], 2)}  
        Prob: {round(r['prob'], 2)}  
        EV: {round(r['ev'], 2)}  
        Bet Size: ${round(r['bet_size'], 2)}  
        Timing: {r['timing']}  
        Book: {r['book']}
        """)

# -----------------------------
# SIDEBAR INFO
# -----------------------------
st.sidebar.title("📊 Info")

st.sidebar.write("Total Games:", len(odds))
st.sidebar.write("Total Plays:", len(results))

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("---")
st.caption("NHL Total Model • Live EV Betting Dashboard")