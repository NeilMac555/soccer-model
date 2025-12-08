import streamlit as st
import numpy as np
import math

# -----------------------------
#   GLOBAL UI SETTINGS
# -----------------------------
st.set_page_config(
    page_title="Soccer Mastery",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .main {background-color:#0d0f13;}
    .stApp {background-color:#0d0f13;}
    div.block-container {padding-top:1rem;}
    h1, h2, h3, h4, h5, h6, p, div {
        color:#ffffff !important;
        font-family: 'Segoe UI', sans-serif;
    }
    .rounded-box {
        background: #1a1d23;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='color:#dd44ff;'>⚽ Soccer Mastery</h1>", unsafe_allow_html=True)


# ============================================================
#           HOME FIELD ADVANTAGE VALUES
# ============================================================

HFA = {
    "Premier League": 0.25,
    "La Liga": 0.30,
    "Serie A": 0.35,
    "Bundesliga": 0.22,
    "Ligue 1": 0.33,
    "Champions League": 0.30,
    "Europa League": 0.30,
    "Neutral Venue": 0.00
}


# ============================================================
#           BAYESIAN STRENGTH CALCULATION
# ============================================================

def compute_strength(xGF, xGA, pitchrank, squad, manager):

    if xGA == 0:
        xGA = 0.01

    xg_component = xGF / xGA
    prior_component = pitchrank / 3.39
    subjective_component = 0.6*(squad/100) + 0.4*(manager/10)

    strength = (
        0.50 * xg_component +
        0.30 * prior_component +
        0.20 * subjective_component
    )

    return strength


# ============================================================
#           SUPREMACY → EXPECTED GOALS MODEL
# ============================================================

def expected_goals_from_supremacy(s):
    base_goals = 1.45
    home_xg = base_goals + (s * 0.60)
    away_xg = base_goals - (s * 0.60)
    return max(home_xg, 0.1), max(away_xg, 0.1)


# ============================================================
#           FIXED POISSON ENGINE (NO ERRORS)
# ============================================================

def match_probabilities(home_xg, away_xg, max_goals=10):
    home_probs = [math.exp(-home_xg) * home_xg**i / math.factorial(i)
                  for i in range(max_goals+1)]
    away_probs = [math.exp(-away_xg) * away_xg**j / math.factorial(j)
                  for j in range(max_goals+1)]

    p_home = 0
    p_away = 0
    p_draw = 0

    for i in range(len(home_probs)):
        for j in range(len(away_probs)):
            p = home_probs[i] * away_probs[j]
            if i > j:
                p_home += p
            elif j > i:
                p_away += p
            else:
                p_draw += p

    return p_home, p_draw, p_away



# ============================================================
#       SIDEBAR NAVIGATION
# ============================================================

menu = st.sidebar.radio(
    "Navigation",
    ["Inputs", "Strength Ratings", "Projection", "Value Detection"]
)


# ============================================================
#                     PAGE 1 — INPUTS
# ============================================================

if menu == "Inputs":
    st.markdown("<h2 style='color:#dd44ff;'>Match Inputs</h2>", unsafe_allow_html=True)

    league = st.selectbox("Select Competition", list(HFA.keys()))

    st.markdown("### Team A — HOME")
    A_xgF = st.number_input("xG For /90", 0.0, 5.0, 0.00, 0.01)
    A_xgA = st.number_input("xG Against /90", 0.0, 5.0, 0.00, 0.01)
    A_pitch = st.number_input("PitchRank (0.35–3.39)", 0.35, 3.39, 1.00, 0.01)
    A_squad = st.slider("Squad Value (0–100)", 0, 100, 50)
    A_man = st.slider("Manager Rating (1–10)", 1, 10, 5)

    st.markdown("### Team B — AWAY")
    B_xgF = st.number_input("xG For /90 ", 0.0, 5.0, 0.00, 0.01)
    B_xgA = st.number_input("xG Against /90 ", 0.0, 5.0, 0.00, 0.01)
    B_pitch = st.number_input("PitchRank (0.35–3.39) ", 0.35, 3.39, 1.00, 0.01)
    B_squad = st.slider("Squad Value (0–100)", 0, 100, 50)
    B_man = st.slider("Manager Rating (1–10)", 1, 10, 5)

    st.session_state["inputs"] = {
        "league": league,
        "A": (A_xgF, A_xgA, A_pitch, A_squad, A_man),
        "B": (B_xgF, B_xgA, B_pitch, B_squad, B_man)
    }


# ============================================================
#              PAGE 2 — STRENGTH RATINGS
# ============================================================

elif menu == "Strength Ratings":
    st.markdown("<h2 style='color:#dd44ff;'>Bayesian Team Strengths</h2>", unsafe_allow_html=True)

    if "inputs" not in st.session_state:
        st.warning("Go to *Inputs* first.")
    else:
        A = compute_strength(*st.session_state["inputs"]["A"])
        B = compute_strength(*st.session_state["inputs"]["B"])

        st.markdown(f"""
        <div class='rounded-box'>
            <h3>Team A Strength: <span style='color:#66ffcc;'>{A:.3f}</span></h3>
            <h3>Team B Strength: <span style='color:#66ffcc;'>{B:.3f}</span></h3>
        </div>
        """, unsafe_allow_html=True)


# ============================================================
#              PAGE 3 — MATCH PROJECTION
# ============================================================

elif menu == "Projection":
    st.markdown("<h2 style='color:#dd44ff;'>Match Projection</h2>", unsafe_allow_html=True)

    if "inputs" not in st.session_state:
        st.warning("Go to *Inputs* first.")
    else:
        league = st.session_state["inputs"]["league"]

        A_strength = compute_strength(*st.session_state["inputs"]["A"])
        B_strength = compute_strength(*st.session_state["inputs"]["B"])

        supremacy = A_strength - B_strength + HFA[league]
        home_xg, away_xg = expected_goals_from_supremacy(supremacy)

        pH, pD, pA = match_probabilities(home_xg, away_xg)

        st.markdown(f"""
        <div class='rounded-box'>
            <h3>Supremacy: {supremacy:.3f}</h3>
            <h3>Expected Goals → Home {home_xg:.2f} | Away {away_xg:.2f}</h3>

            <h3>Win Probabilities</h3>
            Home: {pH*100:.1f}%<br>
            Draw: {pD*100:.1f}%<br>
            Away: {pA*100:.1f}%
        </div>
        """, unsafe_allow_html=True)


# ============================================================
#              PAGE 4 — VALUE DETECTION
# ============================================================

elif menu == "Value Detection":
    st.markdown("<h2 style='color:#dd44ff;'>Value Detection vs Pinnacle</h2>", unsafe_allow_html=True)

    if "inputs" not in st.session_state:
        st.warning("Go to Inputs first.")
    else:
        home_o = st.number_input("Home Odds", 1.01, 20.0, 2.00)
        draw_o = st.number_input("Draw Odds", 1.01, 20.0, 3.50)
        away_o = st.number_input("Away Odds", 1.01, 20.0, 3.75)

        A_strength = compute_strength(*st.session_state["inputs"]["A"])
        B_strength = compute_strength(*st.session_state["inputs"]["B"])
        league = st.session_state["inputs"]["league"]

        supremacy = A_strength - B_strength + HFA[league]
        h_xg, a_xg = expected_goals_from_supremacy(supremacy)
        pH, pD, pA = match_probabilities(h_xg, a_xg)

        fair_H = 1/pH
        fair_D = 1/pD
        fair_A = 1/pA

        st.markdown(f"""
        <div class='rounded-box'>
            <h3>Fair Odds:</h3>
            Home {fair_H:.2f} | Draw {fair_D:.2f} | Away {fair_A:.2f}
        </div>
        """, unsafe_allow_html=True)
