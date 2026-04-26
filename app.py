import streamlit as st
from data.fetch_odds import get_odds
from model.predict import run_model
from streamlit_autorefresh import st_autorefresh

st.set_page_config(layout="wide")
st.title("🏒 NHL SHARP MODEL")

# auto refresh every 30s
st_autorefresh(interval=30000)

@st.cache_data(ttl=300)
def load_data():
    return run_model(get_odds())

results = load_data()

st.markdown("## 🔥 TOP PLAYS")

for r in results[:10]:
    st.markdown(f"""
    ### {r['game']}
    Line: {r['line']}  
    Model: {round(r['projection'],2)}  
    EV: {round(r['ev'],2)}  
    Bet Size: ${round(r['bet_size'],2)}  
    Timing: {r['timing']}  
    Book: {r['book']}
    """)