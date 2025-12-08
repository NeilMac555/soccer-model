import streamlit as st
import numpy as np
import math

# --------------------------------------------------------
# INITIALIZE SESSION STATE (persists across page changes)
# --------------------------------------------------------
if 'A_xgF' not in st.session_state:
    st.session_state.A_xgF = 0.0
    st.session_state.A_xgA = 0.0
    st.session_state.A_squad = 50
    st.session_state.A_manager = 5
    st.session_state.A_pitch = 1.0
    
    st.session_state.B_xgF = 0.0
    st.session_state.B_xgA = 0.0
    st.session_state.B_squad = 50
    st.session_state.B_manager = 5
    st.session_state.B_pitch = 1.0
    
    st.session_state.league = "Premier League"

# --------------------------------------------------------
# UI CONFIG
# --------------------------------------------------------
st.set_page_config(
    page_title="Soccer Mastery",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --------------------------------------------------------
# CSS STYLE — Bettin.gs Cyber Minimal UI
# --------------------------------------------------------
st.markdown("""
<style>
    .main {background-color: #0d0f13;}
    .stApp {background-color: #0d0f13;}
    h1, h2, h3, h4, h5, h6, p, div {color: #ffffff !important;}
    .rounded-box {
        background: #1a1d23;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------
# HOME ADVANTAGE SETTINGS (league-dependent)
# --------------------------------------------------------
HFA = {
    "Premier League": 0.25,
    "Champions League / Europa": 0.35,
    "La Liga": 0.30,
    "Serie A": 0.35,
    "Bundesliga": 0.25,
    "Ligue 1": 0.35,
    "Neutral Venue": 0.00,
}

# --------------------------------------------------------
# CORE FUNCTIONS
# --------------------------------------------------------

def compute_strength(xgF, xgA, squad, manager, pitch):
    """
    Bayesian blended strength score 0–5.
    Weights:
        xG: 50%
        Squad Value: 25%
        Manager Rating: 15%
        PitchRank: 10%
    """

    # Normalize components
    xg_term = xgF - xgA
    xg_scaled = 2.5 * (xg_term + 2) / 4   # maps roughly into 0–5 range

    squad_scaled = 5 * (squad / 100)
    manager_scaled = (manager / 10) * 5
    pitch_scaled = (pitch / 3.39) * 5

    strength = (
        0.50 * xg_scaled +
        0.25 * squad_scaled +
        0.15 * manager_scaled +
        0.10 * pitch_scaled
    )

    return round(strength, 3)


def poisson_probs(home_xg, away_xg, max_goals=7):
    """Compute win/draw probabilities using Poisson."""
    p_home = 0
    p_draw = 0
    p_away = 0

    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            p_i = np.exp(-home_xg) * home_xg**i / math.factorial(i)
            p_j = np.exp(-away_xg) * away_xg**j / math.factorial(j)
            p = p_i * p_j

            if i > j:
                p_home += p
            elif i == j:
                p_draw += p
            else:
                p_away += p

    return p_home, p_draw, p_away


def fair_odds(p):
    return round(1 / p, 2) if p > 0 else None


# --------------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------------
with st.sidebar:
    st.header("Navigation")
    page = st.radio("", ["Inputs", "Strength Ratings", "Projection", "Value Detection"])

# --------------------------------------------------------
# PAGE 1 — INPUTS
# --------------------------------------------------------
if page == "Inputs":
    st.title("Match Inputs")

    st.session_state.league = st.selectbox("Select Competition", list(HFA.keys()), index=list(HFA.keys()).index(st.session_state.league))

    colA, colB = st.columns(2)

    with colA:
        st.subheader("Team A — HOME")
        st.session_state.A_xgF = st.number_input("xG For /90", 0.0, 5.0, st.session_state.A_xgF)
        st.session_state.A_xgA = st.number_input("xG Against /90", 0.0, 5.0, st.session_state.A_xgA)
        st.session_state.A_squad = st.slider("Squad Value (0–100)", 0, 100, st.session_state.A_squad)
        st.session_state.A_manager = st.slider("Manager Rating (1–10)", 1, 10, st.session_state.A_manager)
        st.session_state.A_pitch = st.number_input("PitchRank (0.35–3.39)", 0.35, 3.39, st.session_state.A_pitch)

    with colB:
        st.subheader("Team B — AWAY")
        st.session_state.B_xgF = st.number_input("xG For /90 ", 0.0, 5.0, st.session_state.B_xgF, key="b_xgf")
        st.session_state.B_xgA = st.number_input("xG Against /90 ", 0.0, 5.0, st.session_state.B_xgA, key="b_xga")
        st.session_state.B_squad = st.slider("Squad Value (0–100) ", 0, 100, st.session_state.B_squad, key="b_squad")
        st.session_state.B_manager = st.slider("Manager Rating (1–10) ", 1, 10, st.session_state.B_manager, key="b_manager")
        st.session_state.B_pitch = st.number_input("PitchRank (0.35–3.39) ", 0.35, 3.39, st.session_state.B_pitch, key="b_pitch")

    st.success("Inputs updated.")

# --------------------------------------------------------
# PAGE 2 — STRENGTH RATINGS
# --------------------------------------------------------
if page == "Strength Ratings":
    st.title("Bayesian Blended Team Strengths")

    A_strength = compute_strength(st.session_state.A_xgF, st.session_state.A_xgA, st.session_state.A_squad, st.session_state.A_manager, st.session_state.A_pitch)
    B_strength = compute_strength(st.session_state.B_xgF, st.session_state.B_xgA, st.session_state.B_squad, st.session_state.B_manager, st.session_state.B_pitch)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="rounded-box">', unsafe_allow_html=True)
        st.subheader("Team A Strength")
        st.metric("Strength Score", A_strength)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="rounded-box">', unsafe_allow_html=True)
        st.subheader("Team B Strength")
        st.metric("Strength Score", B_strength)
        st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------------
# PAGE 3 — MATCH PROJECTION
# --------------------------------------------------------
if page == "Projection":
    st.title("Match Projection")

    A_strength = compute_strength(st.session_state.A_xgF, st.session_state.A_xgA, st.session_state.A_squad, st.session_state.A_manager, st.session_state.A_pitch)
    B_strength = compute_strength(st.session_state.B_xgF, st.session_state.B_xgA, st.session_state.B_squad, st.session_state.B_manager, st.session_state.B_pitch)

    supremacy = A_strength - B_strength + HFA[st.session_state.league]

    home_xg = max(0.2, 1.4 + supremacy * 0.45)
    away_xg = max(0.2, 1.1 - supremacy * 0.40)

    pH, pD, pA = poisson_probs(home_xg, away_xg)

    colH, colD, colA = st.columns(3)
    colH.metric("Home Win %", f"{pH*100:.1f}%")
    colD.metric("Draw %", f"{pD*100:.1f}%")
    colA.metric("Away Win %", f"{pA*100:.1f}%")

    st.subheader("Fair Odds")
    col1, col2, col3 = st.columns(3)
    col1.metric("Home", fair_odds(pH))
    col2.metric("Draw", fair_odds(pD))
    col3.metric("Away", fair_odds(pA))

# --------------------------------------------------------
# PAGE 4 — VALUE DETECTION
# --------------------------------------------------------
if page == "Value Detection":
    st.title("Value Detection vs Pinnacle")

    colH, colD, colA = st.columns(3)
    user_home = colH.number_input("Home Odds", 1.01, 15.0, 2.00)
    user_draw = colD.number_input("Draw Odds", 1.01, 15.0, 3.50)
    user_away = colA.number_input("Away Odds", 1.01, 15.0, 3.75)

    A_strength = compute_strength(st.session_state.A_xgF, st.session_state.A_xgA, st.session_state.A_squad, st.session_state.A_manager, st.session_state.A_pitch)
    B_strength = compute_strength(st.session_state.B_xgF, st.session_state.B_xgA, st.session_state.B_squad, st.session_state.B_manager, st.session_state.B_pitch)

    supremacy = A_strength - B_strength + HFA[st.session_state.league]
    home_xg = max(0.2, 1.4 + supremacy * 0.45)
    away_xg = max(0.2, 1.1 - supremacy * 0.40)

    pH, pD, pA = poisson_probs(home_xg, away_xg)

    fair_H = fair_odds(pH)
    fair_D = fair_odds(pD)
    fair_A = fair_odds(pA)

    st.subheader("Value Summary")
    st.write(f"Home Value: {round(user_home - fair_H, 2)}")
    st.write(f"Draw Value: {round(user_draw - fair_D, 2)}")
    st.write(f"Away Value: {round(user_away - fair_A, 2)}")
