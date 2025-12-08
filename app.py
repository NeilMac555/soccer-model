import streamlit as st
import numpy as np
import math

# --------------------------------------------------------
# INITIALIZE SESSION STATE
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
# ENHANCED CSS STYLE — Neon Cyber Theme
# --------------------------------------------------------
st.markdown("""
<style>
    /* Main background with gradient */
    .main {
        background: linear-gradient(135deg, #0a0e1a 0%, #1a1535 50%, #0f1419 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #0a0e1a 0%, #1a1535 50%, #0f1419 100%);
    }
    
    /* Text colors */
    h1 {
        color: #00f5ff !important;
        font-weight: 800 !important;
        text-shadow: 0 0 20px rgba(0, 245, 255, 0.5);
        font-size: 3rem !important;
        margin-bottom: 2rem !important;
    }
    
    h2 {
        color: #ff00ff !important;
        font-weight: 700 !important;
        text-shadow: 0 0 15px rgba(255, 0, 255, 0.4);
    }
    
    h3 {
        color: #00ff88 !important;
        font-weight: 600 !important;
    }
    
    p, div, span, label {
        color: #e0e0e0 !important;
    }
    
    /* Metric styling with neon glow */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        font-weight: 900 !important;
        color: #00f5ff !important;
        text-shadow: 0 0 25px rgba(0, 245, 255, 0.8);
    }
    
    [data-testid="stMetricLabel"] {
        color: #a0a0ff !important;
        font-size: 1.1rem !important;
        font-weight: 600 !important;
    }
    
    /* Card/Box styling with glassmorphism */
    .rounded-box {
        background: rgba(30, 30, 60, 0.6);
        backdrop-filter: blur(10px);
        padding: 25px;
        border-radius: 16px;
        margin-bottom: 20px;
        border: 2px solid rgba(0, 245, 255, 0.3);
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.4),
            inset 0 0 20px rgba(0, 245, 255, 0.1);
        transition: all 0.3s ease;
    }
    
    .rounded-box:hover {
        border-color: rgba(0, 245, 255, 0.6);
        box-shadow: 
            0 12px 40px rgba(0, 0, 0, 0.5),
            inset 0 0 30px rgba(0, 245, 255, 0.2);
        transform: translateY(-2px);
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #ff00ff 0%, #00f5ff 100%);
        color: white;
        font-weight: 700;
        border: none;
        border-radius: 12px;
        padding: 12px 30px;
        box-shadow: 0 4px 20px rgba(255, 0, 255, 0.4);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        box-shadow: 0 6px 30px rgba(255, 0, 255, 0.6);
        transform: translateY(-2px);
    }
    
    /* Input styling */
    .stNumberInput>div>div>input,
    .stSelectbox>div>div>select {
        background: rgba(20, 20, 40, 0.8) !important;
        color: #00f5ff !important;
        border: 2px solid rgba(0, 245, 255, 0.3) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    
    /* Slider styling */
    .stSlider>div>div>div>div {
        background: linear-gradient(90deg, #ff00ff 0%, #00f5ff 100%) !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1535 0%, #0a0e1a 100%);
        border-right: 2px solid rgba(0, 245, 255, 0.3);
    }
    
    /* Radio buttons */
    .stRadio>div>label>div>p {
        color: #00f5ff !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
    }
    
    /* Success/Info boxes */
    .stSuccess {
        background: rgba(0, 255, 136, 0.15) !important;
        border: 2px solid #00ff88 !important;
        border-radius: 12px !important;
        color: #00ff88 !important;
    }
    
    /* Custom value cards */
    .value-positive {
        background: linear-gradient(135deg, rgba(0, 255, 136, 0.2) 0%, rgba(0, 200, 100, 0.1) 100%);
        border: 2px solid #00ff88;
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
        box-shadow: 0 0 20px rgba(0, 255, 136, 0.3);
    }
    
    .value-negative {
        background: linear-gradient(135deg, rgba(255, 50, 50, 0.2) 0%, rgba(200, 0, 0, 0.1) 100%);
        border: 2px solid #ff3232;
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
        box-shadow: 0 0 20px rgba(255, 50, 50, 0.3);
    }
    
    .value-neutral {
        background: linear-gradient(135deg, rgba(100, 100, 255, 0.2) 0%, rgba(50, 50, 150, 0.1) 100%);
        border: 2px solid #6464ff;
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
        box-shadow: 0 0 20px rgba(100, 100, 255, 0.3);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------
# HOME ADVANTAGE SETTINGS
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
    xg_term = xgF - xgA
    xg_scaled = 2.5 * (xg_term + 2) / 4
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
    st.markdown("## ⚡ Navigation")
    page = st.radio("", ["🎯 Inputs", "💪 Strength Ratings", "🔮 Projection", "💎 Value Detection"], label_visibility="collapsed")

# --------------------------------------------------------
# PAGE 1 — INPUTS
# --------------------------------------------------------
if page == "🎯 Inputs":
    st.title("⚽ Match Configuration")
    
    st.markdown('<div class="rounded-box">', unsafe_allow_html=True)
    st.session_state.league = st.selectbox("🏆 Select Competition", list(HFA.keys()), index=list(HFA.keys()).index(st.session_state.league))
    st.markdown('</div>', unsafe_allow_html=True)
    
    colA, colB = st.columns(2)
    
    with colA:
        st.markdown('<div class="rounded-box">', unsafe_allow_html=True)
        st.subheader("🏠 Team A — HOME")
        st.session_state.A_xgF = st.number_input("⚽ xG For /90", 0.0, 5.0, st.session_state.A_xgF)
        st.session_state.A_xgA = st.number_input("🛡️ xG Against /90", 0.0, 5.0, st.session_state.A_xgA)
        st.session_state.A_squad = st.slider("💰 Squad Value", 0, 100, st.session_state.A_squad)
        st.session_state.A_manager = st.slider("👔 Manager Rating", 1, 10, st.session_state.A_manager)
        st.session_state.A_pitch = st.number_input("🏟️ PitchRank", 0.35, 3.39, st.session_state.A_pitch)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with colB:
        st.markdown('<div class="rounded-box">', unsafe_allow_html=True)
        st.subheader("✈️ Team B — AWAY")
        st.session_state.B_xgF = st.number_input("⚽ xG For /90 ", 0.0, 5.0, st.session_state.B_xgF, key="b_xgf")
        st.session_state.B_xgA = st.number_input("🛡️ xG Against /90 ", 0.0, 5.0, st.session_state.B_xgA, key="b_xga")
        st.session_state.B_squad = st.slider("💰 Squad Value ", 0, 100, st.session_state.B_squad, key="b_squad")
        st.session_state.B_manager = st.slider("👔 Manager Rating ", 1, 10, st.session_state.B_manager, key="b_manager")
        st.session_state.B_pitch = st.number_input("🏟️ PitchRank ", 0.35, 3.39, st.session_state.B_pitch, key="b_pitch")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.success("✅ Inputs successfully configured!")

# --------------------------------------------------------
# PAGE 2 — STRENGTH RATINGS
# --------------------------------------------------------
if page == "💪 Strength Ratings":
    st.title("💪 Bayesian Team Strength Analysis")
    
    A_strength = compute_strength(st.session_state.A_xgF, st.session_state.A_xgA, st.session_state.A_squad, st.session_state.A_manager, st.session_state.A_pitch)
    B_strength = compute_strength(st.session_state.B_xgF, st.session_state.B_xgA, st.session_state.B_squad, st.session_state.B_manager, st.session_state.B_pitch)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="rounded-box">', unsafe_allow_html=True)
        st.subheader("🏠 Team A Strength")
        st.metric("Power Rating", f"{A_strength} / 5.0")
        
        # Strength bar visualization
        strength_pct = (A_strength / 5.0) * 100
        st.markdown(f"""
        <div style="background: rgba(0,0,0,0.3); border-radius: 10px; overflow: hidden; height: 30px; margin-top: 15px;">
            <div style="background: linear-gradient(90deg, #ff00ff 0%, #00f5ff 100%); 
                        width: {strength_pct}%; height: 100%; 
                        display: flex; align-items: center; justify-content: center;
                        color: white; font-weight: bold;">
                {strength_pct:.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="rounded-box">', unsafe_allow_html=True)
        st.subheader("✈️ Team B Strength")
        st.metric("Power Rating", f"{B_strength} / 5.0")
        
        strength_pct = (B_strength / 5.0) * 100
        st.markdown(f"""
        <div style="background: rgba(0,0,0,0.3); border-radius: 10px; overflow: hidden; height: 30px; margin-top: 15px;">
            <div style="background: linear-gradient(90deg, #00ff88 0%, #00f5ff 100%); 
                        width: {strength_pct}%; height: 100%; 
                        display: flex; align-items: center; justify-content: center;
                        color: white; font-weight: bold;">
                {strength_pct:.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Comparison
    st.markdown('<div class="rounded-box">', unsafe_allow_html=True)
    st.subheader("⚖️ Head-to-Head Comparison")
    diff = A_strength - B_strength
    if diff > 0:
        st.markdown(f'<p style="color: #00ff88; font-size: 1.3rem; font-weight: bold;">Team A is stronger by {abs(diff):.2f} points</p>', unsafe_allow_html=True)
    elif diff < 0:
        st.markdown(f'<p style="color: #ff00ff; font-size: 1.3rem; font-weight: bold;">Team B is stronger by {abs(diff):.2f} points</p>', unsafe_allow_html=True)
    else:
        st.markdown(f'<p style="color: #00f5ff; font-size: 1.3rem; font-weight: bold;">Teams are evenly matched!</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------------
# PAGE 3 — MATCH PROJECTION
# --------------------------------------------------------
if page == "🔮 Projection":
    st.title("🔮 Match Outcome Projection")
    
    A_strength = compute_strength(st.session_state.A_xgF, st.session_state.A_xgA, st.session_state.A_squad, st.session_state.A_manager, st.session_state.A_pitch)
    B_strength = compute_strength(st.session_state.B_xgF, st.session_state.B_xgA, st.session_state.B_squad, st.session_state.B_manager, st.session_state.B_pitch)
    
    supremacy = A_strength - B_strength + HFA[st.session_state.league]
    home_xg = max(0.2, 1.4 + supremacy * 0.45)
    away_xg = max(0.2, 1.1 - supremacy * 0.40)
    
    pH, pD, pA = poisson_probs(home_xg, away_xg)
    
    # Win probabilities
    st.markdown('<div class="rounded-box">', unsafe_allow_html=True)
    st.subheader("📊 Win Probabilities")
    colH, colD, colA = st.columns(3)
    colH.metric("🏠 Home Win", f"{pH*100:.1f}%")
    colD.metric("🤝 Draw", f"{pD*100:.1f}%")
    colA.metric("✈️ Away Win", f"{pA*100:.1f}%")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Visual probability bars
    st.markdown('<div class="rounded-box">', unsafe_allow_html=True)
    st.subheader("📈 Visual Breakdown")
    
    st.markdown(f"""
    <div style="display: flex; height: 50px; border-radius: 10px; overflow: hidden; box-shadow: 0 0 20px rgba(0,245,255,0.3);">
        <div style="background: linear-gradient(135deg, #00ff88 0%, #00cc66 100%); 
                    width: {pH*100}%; display: flex; align-items: center; justify-content: center; 
                    color: white; font-weight: bold; font-size: 1.2rem;">
            HOME {pH*100:.1f}%
        </div>
        <div style="background: linear-gradient(135deg, #6464ff 0%, #4040dd 100%); 
                    width: {pD*100}%; display: flex; align-items: center; justify-content: center; 
                    color: white; font-weight: bold; font-size: 1.2rem;">
            DRAW {pD*100:.1f}%
        </div>
        <div style="background: linear-gradient(135deg, #ff00ff 0%, #cc00cc 100%); 
                    width: {pA*100}%; display: flex; align-items: center; justify-content: center; 
                    color: white; font-weight: bold; font-size: 1.2rem;">
            AWAY {pA*100:.1f}%
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Fair odds
    st.markdown('<div class="rounded-box">', unsafe_allow_html=True)
    st.subheader("💰 Fair Odds (No Margin)")
    col1, col2, col3 = st.columns(3)
    col1.metric("🏠 Home", fair_odds(pH))
    col2.metric("🤝 Draw", fair_odds(pD))
    col3.metric("✈️ Away", fair_odds(pA))
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Expected goals
    st.markdown('<div class="rounded-box">', unsafe_allow_html=True)
    st.subheader("⚽ Expected Goals")
    col1, col2 = st.columns(2)
    col1.metric("🏠 Home xG", f"{home_xg:.2f}")
    col2.metric("✈️ Away xG", f"{away_xg:.2f}")
    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------------
# PAGE 4 — VALUE DETECTION
# --------------------------------------------------------
if page == "💎 Value Detection":
    st.title("💎 Market Value Detection")
    
    st.markdown('<div class="rounded-box">', unsafe_allow_html=True)
    st.subheader("📊 Market Odds (Pinnacle)")
    colH, colD, colA = st.columns(3)
    user_home = colH.number_input("🏠 Home Odds", 1.01, 15.0, 2.00)
    user_draw = colD.number_input("🤝 Draw Odds", 1.01, 15.0, 3.50)
    user_away = colA.number_input("✈️ Away Odds", 1.01, 15.0, 3.75)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Calculate model probabilities
    A_strength = compute_strength(st.session_state.A_xgF, st.session_state.A_xgA, st.session_state.A_squad, st.session_state.A_manager, st.session_state.A_pitch)
    B_strength = compute_strength(st.session_state.B_xgF, st.session_state.B_xgA, st.session_state.B_squad, st.session_state.B_manager, st.session_state.B_pitch)
    
    supremacy = A_strength - B_strength + HFA[st.session_state.league]
    home_xg = max(0.2, 1.4 + supremacy * 0.45)
    away_xg = max(0.2, 1.1 - supremacy * 0.40)
    
    pH, pD, pA = poisson_probs(home_xg, away_xg)
    
    fair_H = fair_odds(pH)
    fair_D = fair_odds(pD)
    fair_A = fair_odds(pA)
    
    # Calculate value
    value_H = user_home - fair_H
    value_D = user_draw - fair_D
    value_A = user_away - fair_A
    
    st.markdown('<div class="rounded-box">', unsafe_allow_html=True)
    st.subheader("🎯 Value Analysis")
    
    # Home value
    if value_H > 0.15:
        st.markdown(f"""
        <div class="value-positive">
            <h3 style="color: #00ff88 !important; margin: 0;">🏠 HOME BET - STRONG VALUE</h3>
            <p style="font-size: 1.2rem; margin: 10px 0 0 0;">Market: {user_home:.2f} | Fair: {fair_H:.2f} | Edge: +{value_H:.2f} ({(value_H/fair_H)*100:.1f}%)</p>
        </div>
        """, unsafe_allow_html=True)
    elif value_H > 0:
        st.markdown(f"""
        <div class="value-neutral">
            <h3 style="color: #6464ff !important; margin: 0;">🏠 HOME - Slight Value</h3>
            <p style="font-size: 1.1rem; margin: 10px 0 0 0;">Market: {user_home:.2f} | Fair: {fair_H:.2f} | Edge: +{value_H:.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="value-negative">
            <h3 style="color: #ff3232 !important; margin: 0;">🏠 HOME - No Value</h3>
            <p style="font-size: 1.1rem; margin: 10px 0 0 0;">Market: {user_home:.2f} | Fair: {fair_H:.2f} | Edge: {value_H:.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Draw value
    if value_D > 0.15:
        st.markdown(f"""
        <div class="value-positive">
            <h3 style="color: #00ff88 !important; margin: 0;">🤝 DRAW - STRONG VALUE</h3>
            <p style="font-size: 1.2rem; margin: 10px 0 0 0;">Market: {user_draw:.2f} | Fair: {fair_D:.2f} | Edge: +{value_D:.2f} ({(value_D/fair_D)*100:.1f}%)</p>
        </div>
        """, unsafe_allow_html=True)
    elif value_D > 0:
        st.markdown(f"""
        <div class="value-neutral">
            <h3 style="color: #6464ff !important; margin: 0;">🤝 DRAW - Slight Value</h3>
            <p style="font-size: 1.1rem; margin: 10px 0 0 0;">Market: {user_draw:.2f} | Fair: {fair_D:.2f} | Edge: +{value_D:.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="value-negative">
            <h3 style="color: #ff3232 !important; margin: 0;">🤝 DRAW - No Value</h3>
            <p style="font-size: 1.1rem; margin: 10px 0 0 0;">Market: {user_draw:.2f} | Fair: {fair_D:.2f} | Edge: {value_D:.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Away value
    if value_A > 0.15:
        st.markdown(f"""
        <div class="value-positive">
            <h3 style="color: #00ff88 !important; margin: 0;">✈️ AWAY BET - STRONG VALUE</h3>
            <p style="font-size: 1.2rem; margin: 10px 0 0 0;">Market: {user_away:.2f} | Fair: {fair_A:.2f} | Edge: +{value_A:.2f} ({(value_A/fair_A)*100:.1f}%)</p>
        </div>
        """, unsafe_allow_html=True)
    elif value_A > 0:
        st.markdown(f"""
        <div class="value-neutral">
            <h3 style="color: #6464ff !important; margin: 0;">✈️ AWAY - Slight Value</h3>
            <p style="font-size: 1.1rem; margin: 10px 0 0 0;">Market: {user_away:.2f} | Fair: {fair_A:.2f} | Edge: +{value_A:.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="value-negative">
            <h3 style="color: #ff3232 !important; margin: 0;">✈️ AWAY - No Value</h3>
            <p style="font-size: 1.1rem; margin: 10px 0 0 0;">Market: {user_away:.2f} | Fair: {fair_A:.2f} | Edge: {value_A:.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
