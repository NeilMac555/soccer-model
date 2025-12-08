import streamlit as st
import numpy as np
import pandas as pd
from math import exp, factorial

# ===========================================================
# PAGE CONFIG — Clean minimal SaaS aesthetic
# ===========================================================
st.set_page_config(
    page_title="Soccer Mastery",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ===========================================================
# GLOBAL CSS — Rounded cards, clean UI
# ===========================================================
st.markdown("""
<style>

body {
    background-color: #0d1117;
    color: #e6e6e6;
    font-family: 'Inter', sans-serif;
}

h1,h2,h3,h4 {
    font-weight: 600 !important;
    color: #fafafa;
}

.sidebar .sidebar-content {
    background-color: #0d1117 !important;
}

.block-container {
    padding-top: 1rem;
}

.card {
    background: #161b22;
    padding: 18px 22px;
    border-radius: 14px;
    border: 1px solid #1f242d;
    margin-bottom: 18px;
}

.metric-card {
    background: #161b22;
    padding: 20px;
    border-radius: 14px;
    text-align: center;
    border: 1px solid #1f242d;
}

.metric-card h3 {
    font-size: 1rem;
    font-weight: 500;
    color: #c9d1d9;
}

.metric-card p {
    font-size: 1.8rem;
    font-weight: 700;
    color: #58a6ff;
}

table {
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# ===========================================================
# LEAGUE-SPECIFIC HOME FIELD ADVANTAGE
# ===========================================================
HFA = {
    "Premier League": 0.25,
    "La Liga": 0.30,
    "Serie A": 0.35,
    "Bundesliga": 0.22,
    "Ligue 1": 0.32,
    "Champions League": 0.30,
    "Europa League": 0.30,
    "Neutral Venue": 0.00
}

# ===========================================================
# FUNCTIONS
# ===========================================================

def poisson_prob(lmbda, k):
    return (lmbda**k * exp(-lmbda)) / factorial(k)

def compute_correct_score_matrix(lA, lB, max_goals=7):
    matrix = np.zeros((max_goals+1, max_goals+1))
    for i in range(max_goals+1):
        for j in range(max_goals+1):
            matrix[i,j] = poisson_prob(lA, i) * poisson_prob(lB, j)
    return matrix

def expected_goals_from_supremacy(sup):
    base = 1.35
    k = 0.60
    home_xg = base + k*sup
    away_xg = base - k*sup
    return max(home_xg,0.05), max(away_xg,0.05)

def pitchrank_strength(pr):
    return exp(0.55 * (pr - 1))

# ===========================================================
# TITLE
# ===========================================================
st.title("⚽ Soccer Mastery")

# ===========================================================
# SIDEBAR
# ===========================================================
with st.sidebar:
    st.header("Navigation")
    page = st.radio("", ["Inputs", "Strength Ratings", "Projection", "Correct Scores", "Value Detection"])

# ===========================================================
# INPUT PAGE
# ===========================================================
if page == "Inputs":
    st.header("Match Inputs")

    league = st.selectbox("Competition", list(HFA.keys()))

    colA, colB = st.columns(2)
    with colA:
        st.subheader("Home Team")
        A_xgF = st.number_input("xG For per 90", 0.0, 5.0, 0.0, 0.01)
        A_xgA = st.number_input("xG Against per 90", 0.0, 5.0, 0.0, 0.01)
        A_pitch = st.number_input("PitchRank (0.35–3.39)", 0.35, 3.39, 1.00, 0.01)
        A_squad = st.slider("Squad Strength (0–100)", 0, 100, 50)
        A_manager = st.slider("Manager Rating (1–10)", 1, 10, 5)

    with colB:
        st.subheader("Away Team")
        B_xgF = st.number_input("xG For per 90 ", 0.0, 5.0, 0.0, 0.01)
        B_xgA = st.number_input("xG Against per 90 ", 0.0, 5.0, 0.0, 0.01)
        B_pitch = st.number_input("PitchRank (0.35–3.39) ", 0.35, 3.39, 1.00, 0.01)
        B_squad = st.slider("Squad Strength (0–100) ", 0, 100, 50)
        B_manager = st.slider("Manager Rating (1–10) ", 1, 10, 5)

    st.info("Go to Strength Ratings to see blended Bayesian team strengths.")


# ===========================================================
# STRENGTH RATINGS
# ===========================================================
if page == "Strength Ratings":
    st.header("Bayesian Blended Team Strengths")

    # Normalize components
    def compute_strength(xgF, xgA, pitch, squad, manager):
        xg_att = xgF
        xg_def = max(0.1, 1/xgA if xgA > 0 else 1.0)

        pr = pitchrank_strength(pitch)

        squad_norm = squad / 100
        manager_norm = manager / 10

        prior = 0.7*(0.6*xg_att + 0.4*xg_def) + 0.3*(0.5*pr + 0.3*squad_norm + 0.2*manager_norm)

        return prior

    A_strength = compute_strength(A_xgF, A_xgA, A_pitch, A_squad, A_manager)
    B_strength = compute_strength(B_xgF, B_xgA, B_pitch, B_squad, B_manager)

    colA, colB = st.columns(2)
    with colA:
        st.markdown("<div class='metric-card'><h3>Home Strength</h3><p>{:.3f}</p></div>".format(A_strength), unsafe_allow_html=True)
    with colB:
        st.markdown("<div class='metric-card'><h3>Away Strength</h3><p>{:.3f}</p></div>".format(B_strength), unsafe_allow_html=True)


# ===========================================================
# PROJECTION
# ===========================================================
if page == "Projection":
    st.header("Match Projection")

    supremacy = A_strength - B_strength + HFA[league]

    lA, lB = expected_goals_from_supremacy(supremacy)

    st.subheader("Expected Goals")
    col1, col2 = st.columns(2)
    col1.metric("Home xG", f"{lA:.2f}")
    col2.metric("Away xG", f"{lB:.2f}")

    matrix = compute_correct_score_matrix(lA, lB)

    homeP = np.sum(np.triu(matrix,1))
    drawP = np.sum(np.diag(matrix))
    awayP = np.sum(np.tril(matrix,-1))

    st.subheader("Outcome Probabilities")
    col1, col2, col3 = st.columns(3)
    col1.metric("Home Win %", f"{homeP*100:.1f}%")
    col2.metric("Draw %", f"{drawP*100:.1f}%")
    col3.metric("Away Win %", f"{awayP*100:.1f}%")

    st.subheader("Fair Odds")
    col1, col2, col3 = st.columns(3)
    col1.metric("Home", f"{1/homeP:.2f}")
    col2.metric("Draw", f"{1/drawP:.2f}")
    col3.metric("Away", f"{1/awayP:.2f}")

    st.info(f"Most Likely Scoreline: {np.unravel_index(np.argmax(matrix), matrix.shape)[0]} - {np.unravel_index(np.argmax(matrix), matrix.shape)[1]}")


# ===========================================================
# CORRECT SCORES
# ===========================================================
if page == "Correct Scores":
    st.header("Correct Score Probability Grid")

    matrix = compute_correct_score_matrix(
        expected_goals_from_supremacy(A_strength - B_strength + HFA[league])[0],
        expected_goals_from_supremacy(A_strength - B_strength + HFA[league])[1]
    )

    df = pd.DataFrame(matrix, index=[f"{i} goals" for i in range(8)],
                               columns=[f"{j} goals" for j in range(8)])
    st.dataframe(df.style.background_gradient(cmap="Blues"))


# ===========================================================
# VALUE DETECTION
# ===========================================================
if page == "Value Detection":
    st.header("Value Detection vs Pinnacle")

    st.subheader("Market Odds (Pinnacle default)")
    col1, col2, col3 = st.columns(3)
    oddH = col1.number_input("Home Odds", 1.01, 25.0, 2.00)
    oddD = col2.number_input("Draw Odds", 1.01, 25.0, 3.50)
    oddA = col3.number_input("Away Odds", 1.01, 25.0, 3.75)

    supremacy = A_strength - B_strength + HFA[league]
    lA, lB = expected_goals_from_supremacy(supremacy)
    matrix = compute_correct_score_matrix(lA, lB)

    homeP = np.sum(np.triu(matrix,1))
    drawP = np.sum(np.diag(matrix))
    awayP = np.sum(np.tril(matrix,-1))

    market_probs = np.array([1/oddH, 1/oddD, 1/oddA])
    market_probs /= market_probs.sum()

    model_probs = np.array([homeP, drawP, awayP])

    edges = model_probs - market_probs

    st.subheader("Value Signals")
    col1, col2, col3 = st.columns(3)

    col1.metric("Home Edge", f"{edges[0]*100:.2f}%")
    col2.metric("Draw Edge", f"{edges[1]*100:.2f}%")
    col3.metric("Away Edge", f"{edges[2]*100:.2f}%")

    best = np.argmax(edges)
    bets = ["Home", "Draw", "Away"]

    if edges[best] > 0:
        st.success(f"Recommended Bet: **{bets[best]}** (Edge {edges[best]*100:.2f}%)")
    else:
        st.warning("No positive value detected. Market is sharp.")

