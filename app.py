import streamlit as st
import random
import time

# --------------------- PAGE SETUP ---------------------
st.set_page_config(page_title="Probabilistic Roulette", page_icon="🎮", layout="centered")

# --------------------- CSS STYLING ---------------------
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Press Start 2P', cursive !important;
        background-color: #9bbc0f;
        color: #0f380f;
        text-align: center;
    }
    .stButton>button {
        background-color: #306230;
        color: #e0f8cf;
        border: 3px solid #0f380f;
        font-family: 'Press Start 2P', cursive;
        font-size: 12px !important;
        padding: 10px 20px;
        border-radius: 0px;
        transition: all 0.1s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #8bac0f;
        color: black;
    }
    .big-text {
        font-size: 18px !important;
        line-height: 1.8;
    }
    .title {
        font-size: 24px !important;
        color: #0f380f;
    }
    body::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: repeating-linear-gradient(
            rgba(0,0,0,0.05) 0px,
            rgba(0,0,0,0.05) 1px,
            transparent 1px,
            transparent 2px
        );
        z-index: 9999;
        pointer-events: none;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------- TEXT ANIMATION ---------------------
def type_text(text, delay=0.03):
    """Simulate typing animation for story narration."""
    placeholder = st.empty()
    s = ""
    for char in text:
        s += char
        placeholder.markdown(f"<p class='big-text'>{s}</p>", unsafe_allow_html=True)
        time.sleep(delay)

# --------------------- INITIALIZE SESSION STATE ---------------------
if "round" not in st.session_state:
    st.session_state.round = 1
    st.session_state.queue_length = 3  # initial queue
    st.session_state.alive = True
    st.session_state.score = 0

# --------------------- TITLE ---------------------
st.markdown("<br><div class='title'>🎲 PROBABILISTIC ROULETTE 🎲</div><br>", unsafe_allow_html=True)

# --------------------- GAME LOGIC ---------------------
if st.session_state.alive:

    # Queue length can increase with Poisson(λ=1.5)
    arrivals = random.poisson(lam=1.5) if hasattr(random, 'poisson') else int(random.expovariate(1/1.5))
    st.session_state.queue_length += arrivals

    type_text(f"Round {st.session_state.round}: The tavern queue has {st.session_state.queue_length} souls awaiting their fate...")

    # Probability of poison increases slightly each round
    poison_prob = min(0.2 + st.session_state.round * 0.05, 0.8)
    wait_time = random.expovariate(1.0 / (st.session_state.queue_length + 1))

    st.markdown(f"🧍 Queue length: **{st.session_state.queue_length}**")
    st.markdown(f"⏳ Expected wait time (M/M/1): **{wait_time:.2f} units**")
    st.markdown(f"☠️ Poison probability this round: **{poison_prob*100:.1f}%**")

    if st.button("Take the Shot 💥"):
        st.session_state.round += 1
        st.session_state.queue_length = max(1, st.session_state.queue_length - 1)
        shot = random.random()
        if shot < poison_prob:
            type_text("💀 The chamber clicks... then silence. You feel your breath fade. Game over.", 0.02)
            st.session_state.alive = False
        else:
            type_text("🎯 You survive! The crowd roars. Another stranger steps up.", 0.02)
            st.session_state.score += 1
            st.rerun()

else:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"🏆 Final Score: **{st.session_state.score} survivors**")
    if st.button("🔁 Restart Game"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# --------------------- FOOTER ---------------------
st.markdown("<br><hr><p style='font-size:10px'>Made with ❤️ in Streamlit · IIT KGP Probability & Statistics Game</p>", unsafe_allow_html=True)
