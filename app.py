import streamlit as st
import numpy as np
import pandas as pd
from math import exp, factorial

# ===========================================================
# PAGE CONFIG
# ===========================================================
st.set_page_config(
    page_title="Soccer Model 3.0 — Bayesian Engine",
    layout="wide"
)

# ===========================================================
# CYBERPUNK NEON PURPLE/ORANGE THEME
# ===========================================================
st.markdown("""
<style>

body {
    background-color: #0a0014;
    color: #e0d7ff;
}

section.main {
    background-color: #0a0014 !important;
}

h1, h2, h3, h4, h5 {
    color: #ff9fff !important;
    font-weight: 700 !important;
    text-shadow: 0 0 12px #ff38ff;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 2rem;
}

.stTabs [data-baseweb="tab"] {
    font-size: 1.2rem;
    padding: 0.75rem 1.25rem;
    color: #ffaaff;
    border-radius: 8px;
    background: rgba(255, 120, 255, 0.08);
    transition: 0.3s;
}

.stTabs [aria-selected="true"] {
    color: #ff9fff !important;
    background: rgba(255, 120, 255, 0.20);
    border-bottom: 3px solid #ff38ff !important;
    text-shadow: 0 0 10px #ff38ff;
}

[data-testid="stMetricValue"] {
    color: #ff8c42 !important;
    text-shadow: 0px 0px 12px #ff8c42;
    font-weight: 900 !important;
    font-size: 2.1rem !important;
}

</style>
""", unsafe_allow_html=True)

# ===========================================================
# LEAGUE PARAMETERS (calibrated)
# ===========================================================

LEAGUES = {
    "Premier League":      {"base_rate": 1.55, "hfa": 1.09, "rho": -0.07},
    "Serie A":             {"base_rate": 1.45, "hfa": 1.12, "rho": -0.04},
    "La Liga":             {"base_rate": 1.27, "hfa": 1.10, "rho": -0.03},
    "Bundesliga":          {"base_rate": 1.70, "hfa": 1.08, "rho": -0.10},
    "Ligue 1":             {"base_rate": 1.45, "hfa": 1.11, "rho": -0.06},
    "European Competitions": {"base_rate": 1.58, "hfa": 1.13, "rho": -0.05},
    "Neutral Venue":       {"base_rate": 1.50, "hfa": 1.00, "rho": -0.05}
}

# ===========================================================
# BAYESIAN TEAM STRENGTH MODEL
# ===========================================================

def bayesian_strength(xG_for, xG_against, squad_value, manager_rating, league_avg):
    """
    SPI-STYLE PRIOR:
    prior = 0.6 * squad_value_norm + 0.4 * manager_norm
    """

    squad_norm = squad_value / 100
    manager_norm = manager_rating / 10

    prior = 0.6 * squad_norm + 0.4 * manager_norm

    # xG strength relative to league
    att_xg = xG_for / league_avg
    def_xg = league_avg / xG_against if xG_against > 0 else 1.0

    # Combine with priors:
    # Fast decay simulated by giving xG less weight (0.55) and priors strong weight (0.45)
    attack_strength = (0.55 * att_xg) + (0.45 * prior)
    defense_strength = (0.55 * def_xg) + (0.45 * prior)

    # Moderate shrinkage
    attack_strength = 1 + 0.6*(attack_strength - 1)
    defense_strength = 1 + 0.6*(defense_strength - 1)

    return attack_strength, defense_strength


# ===========================================================
# POISSON + DIXON-COLES
# ===========================================================

def poisson_prob(lmbda, k):
    return (lmbda**k * exp(-lmbda)) / factorial(k)

def dixon_coles(lambda_home, lambda_away, rho, max_goals=7):
    matrix = np.zeros((max_goals+1, max_goals+1))

    for i in range(max_goals+1):
        for j in range(max_goals+1):
            corr = 1.0

            if i == 0 and j == 0:
                corr = 1 - rho
            elif i == 0 and j == 1:
                corr = 1 + rho
            elif i == 1 and j == 0:
                corr = 1 + rho
            elif i == 1 and j == 1:
                corr = 1 - rho

            matrix[i, j] = poisson_prob(lambda_home, i) * poisson_prob(lambda_away, j) * corr

    return matrix


# ===========================================================
# UI LAYOUT
# ===========================================================

st.title("⚽ Soccer Model 3.0 — SPI Bayesian Engine (Cyberpunk Edition)")

tabs = st.tabs(["📝 Inputs", "📊 Strengths", "🔮 Projection", "🧮 Correct Scores", "💸 Value Detection"])


# ===========================================================
# TAB 1 — INPUTS
# ===========================================================
with tabs[0]:
    st.header("Match Inputs")

    league = st.selectbox("Select Competition", list(LEAGUES.keys()))

    colA, colB = st.columns(2)

    with colA:
        st.subheader("Team A — HOME")

        A_xgf = st.number_input("xG For /90", value=0.00, step=0.01)
        A_xga = st.number_input("xG Against /90", value=0.00, step=0.01)
        A_value = st.slider("Squad Value (0–100)", 0, 100, 0)
        A_manager = st.slider("Manager Rating (1–10)", 1, 10, 5)

    with colB:
        st.subheader("Team B — AWAY")

        B_xgf = st.number_input("xG For /90 ", value=0.00, step=0.01)
        B_xga = st.number_input("xG Against /90 ", value=0.00, step=0.01)
        B_value = st.slider("Squad Value (0–100) ", 0, 100, 0)
        B_manager = st.slider("Manager Rating (1–10) ", 1, 10, 5)


# ===========================================================
# TAB 2 — STRENGTHS
# ===========================================================
with tabs[1]:
    st.header("Bayesian Team Strengths")

    lg = LEAGUES[league]
    league_avg = lg["base_rate"]

    attA, defA = bayesian_strength(A_xgf, A_xga, A_value, A_manager, league_avg)
    attB, defB = bayesian_strength(B_xgf, B_xga, B_value, B_manager, league_avg)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Team A (Home)")
        st.metric("Attack Strength", f"{attA:.3f}")
        st.metric("Defense Strength", f"{defA:.3f}")

    with col2:
        st.subheader("Team B (Away)")
        st.metric("Attack Strength", f"{attB:.3f}")
        st.metric("Defense Strength", f"{defB:.3f}")


# ===========================================================
# TAB 3 — PROJECTION
# ===========================================================
with tabs[2]:
    st.header("Match Projection (Poisson + Dixon–Coles)")

    # Expected goals
    lambda_home = league_avg * attA * defB * lg["hfa"]
    lambda_away = league_avg * attB * defA

    matrix = dixon_coles(lambda_home, lambda_away, lg["rho"])

    homeP = np.sum(np.triu(matrix, k=1))
    awayP = np.sum(np.tril(matrix, k=-1))
    drawP = np.sum(np.diag(matrix))

    colp1, colp2, colp3 = st.columns(3)
    colp1.metric("Home Win %", f"{homeP*100:.1f}%")
    colp2.metric("Draw %", f"{drawP*100:.1f}%")
    colp3.metric("Away Win %", f"{awayP*100:.1f}%")

    st.subheader("Fair Odds")
    colf1, colf2, colf3 = st.columns(3)
    colf1.metric("Home", f"{1/homeP:.2f}")
    colf2.metric("Draw", f"{1/drawP:.2f}")
    colf3.metric("Away", f"{1/awayP:.2f}")

    st.subheader("Expected Goals")
    colEG1, colEG2 = st.columns(2)
    colEG1.metric("λ Home", f"{lambda_home:.2f}")
    colEG2.metric("λ Away", f"{lambda_away:.2f}")


# ===========================================================
# TAB 4 — CORRECT SCORES
# ===========================================================
with tabs[3]:
    st.header("Correct Score Probabilities")

    df = pd.DataFrame(matrix,
        index=[f"{i} goals" for i in range(matrix.shape[0])],
        columns=[f"{j} goals" for j in range(matrix.shape[1])]
    )

    st.dataframe(df.style.highlight_max(axis=None, color="#ff8c42"))


# ===========================================================
# TAB 5 — VALUE DETECTION
# ===========================================================
with tabs[4]:
    st.header("Value Detection vs Market")

    colO1, colO2, colO3 = st.columns(3)
    oddH = colO1.number_input("Home Odds", value=0.00, step=0.01)
    oddD = colO2.number_input("Draw Odds", value=0.00, step=0.01)
    oddA = colO3.number_input("Away Odds", value=0.00, step=0.01)

    if oddH > 0 and oddD > 0 and oddA > 0:

        rawH = 1/oddH
        rawD = 1/oddD
        rawA = 1/oddA

        margin = rawH + rawD + rawA

        MH = rawH / margin
        MD = rawD / margin
        MA = rawA / margin

        st.subheader("Market-Implied Probabilities")
        colM1, colM2, colM3 = st.columns(3)
        colM1.metric("Home", f"{MH*100:.1f}%")
        colM2.metric("Draw", f"{MD*100:.1f}%")
        colM3.metric("Away", f"{MA*100:.1f}%")

        # Edges
        valH = homeP - MH
        valD = drawP - MD
        valA = awayP - MA

        st.subheader("Value Signals")

        if valH > 0:
            st.success(f"VALUE ON HOME — Edge {valH:.4f}")
        if valD > 0:
            st.success(f"VALUE ON DRAW — Edge {valD:.4f}")
        if valA > 0:
            st.success(f"VALUE ON AWAY — Edge {valA:.4f}")

        if valH <= 0 and valD <= 0 and valA <= 0:
            st.warning("⚠️ No value detected — Market is sharp.")

