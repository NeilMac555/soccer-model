import streamlit as st
import numpy as np
import math

# --------------------------------------------------------
# GLOBAL UI SETTINGS
# --------------------------------------------------------
st.set_page_config(
    page_title="Soccer Mastery",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --------------------------------------------------------
# THEME (bettin.gs-style clean dark UI)
# --------------------------------------------------------
st.markdown("""
<style>
    .main {background-color:#0d0f13;}
    .stApp {background-color:#0d0f13;}
    h1, h2, h3, h4, h5, h6, p, div, span {
        color:#ffffff !important;
        font-family:'Segoe UI', sans-serif;
    }
    .rounded-box {
        background: #1a1d23;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------
# HOME FIELD ADVANTAGE (league presets)
# --------------------------------------------------------
HFA = {
    "Premier League": 0.25,
    "Serie A": 0.38,
    "La Liga": 0.30,
    "Bundesliga": 0.22,
    "Ligue 1": 0.33,
    "Champions League / Europa": 0.35,
    "Neutral Venue": 0.00
}

# --------------------------------------------------------
# TEAM STRENGTH BLENDER
# (xG, squad value, manager, PitchRank)
# --------------------------------------------------------
def compute_strength(xg_for, xg_against, squad, manager, pitchrank):
    """
    Returns a single strength number.
    Weighted blend of:
    - xGF / xGA ratio
    - Squad value
    - Manager rating
    - PitchRank injection
    """

    if xg_against == 0:
        xga = 0.0001
    else:
        xga = xg_against

    xg_component = (xg_for / xga)

    squad_component = squad / 100  
    manager_component = manager / 10  

    # PitchRank: expected range 0.35–3.39  
    pitch_component = pitchrank / 3.39  

    strength = (
        0.40 * xg_component +
        0.25 * squad_component +
        0.15 * manager_component +
        0.20 * pitch_component
    )

    return strength

# --------------------------------------------------------
# POISSON MATCH MODEL (correct implementation)
# --------------------------------------------------------
def poisson_prob(lmbda, k):
    """Probability of scoring exactly k goals."""
    return np.exp(-lmbda) * (lmbda ** k) / math.factorial(k)

def match_probs(home_xg, away_xg):
    """Returns probabilities for Home, Draw, Away."""
    max_goals = 10
    P = np.zeros((max_goals, max_goals))

    for i in range(max_goals):
        for j in range(max_goals):
            P[i][j] = poisson_prob(home_xg, i) * poisson_prob(away_xg, j)

    p_home = np.sum(P[np.triu_indices(max_goals, 1)])
    p_away = np.sum(P[np.tril_indices(max_goals, -1)])
    p_draw = np.sum(np.diag(P))

    return p_home, p_draw, p_away

# --------------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------------
page = st.sidebar.radio(
    "Navigation",
    ["Inputs", "Strength Ratings", "Projection", "Value Detection"]
)


# --------------------------------------------------------
# PAGE: INPUTS
# --------------------------------------------------------
if page == "Inputs":
    st.title("Match Inputs")
    st.markdown("### Enter team data to generate predictions")

    league = st.selectbox("Select Competition", list(HFA.keys()))

    colA, colB = st.columns(2)

    with colA:
        st.subheader("Team A — HOME")
        A_xgF = st.number_input("xG For /90", 0.0, 5.0, 0.0)
        A_xgA = st.number_input("xG Against /90", 0.0, 5.0, 0.0)
        A_squad = st.slider("Squad Value (0–100)", 0, 100, 50)
        A_manager = st.slider("Manager Rating (1–10)", 1, 10, 5)
        A_pitch = st.number_input("PitchRank (0.35–3.39)", 0.35, 3.39, 1.0)

    with colB:
        st.subheader("Team B — AWAY")
        B_xgF = st.number_input("xG For /90", 0.0, 5.0, 0.0, key="bxgf")
        B_xgA = st.number_input("xG Against /90", 0.0, 5.0, 0.0, key="bxga")
        B_squad = st.slider("Squad Value (0–100)", 0, 100, 50, key="bsq")
        B_manager = st.slider("Manager Rating (1–10)", 1, 10, 5, key="bman")
        B_pitch = st.number_input("PitchRank (0.35–3.39)", 0.35, 3.39, 1.0, key="bpitch")

    st.success("Inputs updated. Select another tab to continue.")


# --------------------------------------------------------
# PAGE: STRENGTH RATINGS
# --------------------------------------------------------
if page == "Strength Ratings":
    st.title("Bayesian Blended Team Strengths")

    A_strength = compute_strength(A_xgF, A_xgA, A_squad, A_manager, A_pitch)
    B_strength = compute_strength(B_xgF, B_xgA, B_squad, B_manager, B_pitch)

    col1, col2 = st.columns(2)
    col1.metric("Team A Strength", f"{A_strength:.3f}")
    col2.metric("Team B Strength", f"{B_strength:.3f}")


# --------------------------------------------------------
# PAGE: MATCH PROJECTION
# --------------------------------------------------------
if page == "Projection":
    st.title("Match Projection")

    A_strength = compute_strength(A_xgF, A_xgA, A_squad, A_manager, A_pitch)
    B_strength = compute_strength(B_xgF, B_xgA, B_squad, B_manager, B_pitch)

    suprem = A_strength - B_strength + HFA[league]

    home_xg = max(0.01, 1.35 + suprem * 0.60)
    away_xg = max(0.01, 1.35 - suprem * 0.60)

    pH, pD, pA = match_probs(home_xg, away_xg)

    col1, col2, col3 = st.columns(3)
    col1.metric("Home Win %", f"{pH*100:.1f}%")
    col2.metric("Draw %", f"{pD*100:.1f}%")
    col3.metric("Away Win %", f"{pA*100:.1f}%")

    st.markdown("### Expected Goals")
    col4, col5 = st.columns(2)
    col4.metric("Home xG", f"{home_xg:.2f}")
    col5.metric("Away xG", f"{away_xg:.2f}")


# --------------------------------------------------------
# PAGE: VALUE DETECTION
# --------------------------------------------------------
if page == "Value Detection":
    st.title("Value Detection vs Pinnacle")

    col1, col2, col3 = st.columns(3)
    home_odds = col1.number_input("Home Odds", 1.01, 20.0, 2.00)
    draw_odds = col2.number_input("Draw Odds", 1.01, 20.0, 3.50)
    away_odds = col3.number_input("Away Odds", 1.01, 20.0, 3.75)

    A_strength = compute_strength(A_xgF, A_xgA, A_squad, A_manager, A_pitch)
    B_strength = compute_strength(B_xgF, B_xgA, B_squad, B_manager, B_pitch)

    suprem = A_strength - B_strength + HFA[league]

    home_xg = max(0.01, 1.35 + suprem * 0.60)
    away_xg = max(0.01, 1.35 - suprem * 0.60)

    pH, pD, pA = match_probs(home_xg, away_xg)

    fairH = 1 / pH
    fairD = 1 / pD
    fairA = 1 / pA

    col4, col5, col6 = st.columns(3)
    col4.metric("Fair Home Odds", f"{fairH:.2f}")
    col5.metric("Fair Draw Odds", f"{fairD:.2f}")
    col6.metric("Fair Away Odds", f"{fairA:.2f}")

    st.subheader("Value Signals")
    if home_odds > fairH:
        st.success("Home team is undervalued!")
    if draw_odds > fairD:
        st.success("Draw is undervalued!")
    if away_odds > fairA:
        st.success("Away team is undervalued!")
