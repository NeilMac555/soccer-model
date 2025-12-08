import streamlit as st
import numpy as np

# -----------------------------
#     GLOBAL PAGE SETTINGS
# -----------------------------
st.set_page_config(
    page_title="Soccer Mastery",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Title
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
#        1 — ENGINE: HFA, Strength, Supremacy, Poisson
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

def compute_strength(xGF, xGA, pitchrank, squad, manager):
    if xGA == 0:
        xGA = 0.01

    xg_component = xGF / xGA
    prior_component = pitchrank / 3.39  # normalize 0.35–3.39 range
    subjective_component = 0.6*(squad/100) + 0.4*(manager/10)

    strength = (
        0.50 * xg_component +
        0.30 * prior_component +
        0.20 * subjective_component
    )

    return strength


def expected_goals_from_supremacy(s):
    base_goals = 1.45
    home_xg = base_goals + (s * 0.60)
    away_xg = base_goals - (s * 0.60)
    return max(home_xg, 0.1), max(away_xg, 0.1)


def match_probabilities(home_xg, away_xg, max_goals=10):
    probs = np.zeros((max_goals + 1, max_goals + 1))

    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            p_i = np.exp(-home_xg) * home_xg**i / np.math.factorial(i)
            p_j = np.exp(-away_xg) * away_xg**j / np.math.factorial(j)
            probs[i, j] = p_i * p_j

    home = probs[np.triu_indices(max_goals+1, k=1)].sum()
    away = probs[np.tril_indices(max_goals+1, k=-1)].sum()
    draw = np.trace(probs)

    return home, draw, away



# ============================================================
#                     SIDEBAR NAVIGATION
# ============================================================

menu = st.sidebar.radio(
    "Navigation",
    ["Inputs", "Strength Ratings", "Projection", "Correct Scores", "Value Detection"]
)

# ============================================================
#                         PAGE 1: Inputs
# ============================================================

if menu == "Inputs":
    st.markdown("<h2 style='color:#dd44ff;'>Match Inputs</h2>", unsafe_allow_html=True)

    league = st.selectbox("Select Competition", list(HFA.keys()))

    st.markdown("### Team A — HOME")
    A_xgF = st.number_input("xG For /90", 0.0, 5.0, 0.0, 0.01)
    A_xgA = st.number_input("xG Against /90", 0.0, 5.0, 0.0, 0.01)
    A_pitch = st.number_input("PitchRank (0.35–3.39)", 0.35, 3.39, 1.0, 0.01)
    A_squad = st.slider("Squad Value (0–100)", 0, 100, 50)
    A_manager = st.slider("Manager Rating (1–10)", 1, 10, 5)

    st.markdown("### Team B — AWAY")
    B_xgF = st.number_input("xG For /90 ", 0.0, 5.0, 0.0, 0.01)
    B_xgA = st.number_input("xG Against /90 ", 0.0, 5.0, 0.0, 0.01)
    B_pitch = st.number_input("PitchRank (0.35–3.39) ", 0.35, 3.39, 1.0, 0.01)
    B_squad = st.slider("Squad Value (0–100) ", 0, 100, 50)
    B_manager = st.slider("Manager Rating (1–10) ", 1, 10, 5)

    st.session_state["inputs"] = {
        "league": league,
        "A": (A_xgF, A_xgA, A_pitch, A_squad, A_manager),
        "B": (B_xgF, B_xgA, B_pitch, B_squad, B_manager)
    }



# ============================================================
#             PAGE 2: Strength Ratings (Bayesian)
# ============================================================

elif menu == "Strength Ratings":
    st.markdown("<h2 style='color:#dd44ff;'>Bayesian Strength Ratings</h2>", unsafe_allow_html=True)

    if "inputs" not in st.session_state:
        st.warning("Go to *Inputs* first.")
    else:
        A_xgF, A_xgA, A_pitch, A_squad, A_man = st.session_state["inputs"]["A"]
        B_xgF, B_xgA, B_pitch, B_squad, B_man = st.session_state["inputs"]["B"]

        A_strength = compute_strength(A_xgF, A_xgA, A_pitch, A_squad, A_man)
        B_strength = compute_strength(B_xgF, B_xgA, B_pitch, B_squad, B_man)

        st.markdown(f"""
        <div class='rounded-box'>
            <h3>Team A Strength: <span style='color:#66ffcc;'>{A_strength:.3f}</span></h3>
            <h3>Team B Strength: <span style='color:#66ffcc;'>{B_strength:.3f}</span></h3>
        </div>
        """, unsafe_allow_html=True)



# ============================================================
#                    PAGE 3: Projection
# ============================================================

elif menu == "Projection":
    st.markdown("<h2 style='color:#dd44ff;'>Match Projection</h2>", unsafe_allow_html=True)

    if "inputs" not in st.session_state:
        st.warning("Go to *Inputs* first.")
    else:
        league = st.session_state["inputs"]["league"]
        A_vals = st.session_state["inputs"]["A"]
        B_vals = st.session_state["inputs"]["B"]

        A_strength = compute_strength(*A_vals)
        B_strength = compute_strength(*B_vals)

        supremacy = A_strength - B_strength + HFA[league]
        home_xg, away_xg = expected_goals_from_supremacy(supremacy)
        pH, pD, pA = match_probabilities(home_xg, away_xg)

        st.markdown(f"""
        <div class='rounded-box'>
            <h3>Supremacy: <span style='color:#66ffcc;'>{supremacy:.3f}</span></h3>
            <h3>Expected Goals — Home: {home_xg:.2f} | Away: {away_xg:.2f}</h3>
            <h3>Probabilities:</h3>
            Home {pH*100:.1f}% &nbsp;&nbsp; Draw {pD*100:.1f}% &nbsp;&nbsp; Away {pA*100:.1f}%
        </div>
        """, unsafe_allow_html=True)



# ============================================================
#                    PAGE 4: Correct Scores
# ============================================================

elif menu == "Correct Scores":
    st.markdown("<h2 style='color:#dd44ff;'>Correct Score Probabilities</h2>", unsafe_allow_html=True)

    if "inputs" not in st.session_state:
        st.warning("Go to *Inputs* first.")
    else:
        A_vals = st.session_state["inputs"]["A"]
        B_vals = st.session_state["inputs"]["B"]
        league = st.session_state["inputs"]["league"]

        A_strength = compute_strength(*A_vals)
        B_strength = compute_strength(*B_vals)
        supremacy = A_strength - B_strength + HFA[league]

        home_xg, away_xg = expected_goals_from_supremacy(supremacy)

        st.markdown("<h3>Correct Score Matrix</h3>", unsafe_allow_html=True)

        table = ""
        for i in range(0, 6):
            row = ""
            for j in range(0, 6):
                p_i = np.exp(-home_xg) * home_xg**i / np.math.factorial(i)
                p_j = np.exp(-away_xg) * away_xg**j / np.math.factorial(j)
                row += f"{100*p_i*p_j:.2f}%  "
            table += row + "\n"

        st.text(table)



# ============================================================
#                    PAGE 5: Value Detection
# ============================================================

elif menu == "Value Detection":
    st.markdown("<h2 style='color:#dd44ff;'>Value Detection vs Pinnacle</h2>", unsafe_allow_html=True)

    if "inputs" not in st.session_state:
        st.warning("Go to *Inputs* first.")
    else:
        home_odds = st.number_input("Home Odds", 1.01, 20.0, 2.00)
        draw_odds = st.number_input("Draw Odds", 1.01, 20.0, 3.50)
        away_odds = st.number_input("Away Odds", 1.01, 20.0, 3.75)

        A_vals = st.session_state["inputs"]["A"]
        B_vals = st.session_state["inputs"]["B"]
        league = st.session_state["inputs"]["league"]

        A_strength = compute_strength(*A_vals)
        B_strength = compute_strength(*B_vals)
        supremacy = A_strength - B_strength + HFA[league]

        home_xg, away_xg = expected_goals_from_supremacy(supremacy)
        pH, pD, pA = match_probabilities(home_xg, away_xg)

        fair_home = 1 / pH
        fair_draw = 1 / pD
        fair_away = 1 / pA

        st.markdown(f"""
        <div class='rounded-box'>
            <h3>Fair Odds:</h3>
            Home {fair_home:.2f} | Draw {fair_draw:.2f} | Away {fair_away:.2f}
        </div>
        """, unsafe_allow_html=True)

