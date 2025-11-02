import streamlit as st
import numpy as np
import random
import time

# =========================
# 🎨 GameBoy Theme Styling
# =========================
st.set_page_config(page_title="λ: The Last Queue", layout="centered")

st.markdown(
    """
    <style>
    body {
        background-color: #1a2d1a;
        color: #a6f58f;
        font-family: 'Press Start 2P', monospace;
        text-align: center;
    }
    .title {
        font-size: 22px;
        color: #9aff8f;
        text-shadow: 0 0 10px #9aff8f;
        margin-bottom: 20px;
    }
    .text {
        font-size: 14px;
        line-height: 1.8;
    }
    .blink {
        animation: blink 1s step-start infinite;
    }
    @keyframes blink { 50% { opacity: 0; } }
    </style>

    <link href="https://fonts.cdnfonts.com/css/press-start-2p" rel="stylesheet">
    """,
    unsafe_allow_html=True
)

# =========================
# 🧠 Initialize Session State
# =========================
if "lmbd" not in st.session_state:
    st.session_state.lmbd = 0.7
if "mu" not in st.session_state:
    st.session_state.mu = 1.1
if "toxicity" not in st.session_state:
    st.session_state.toxicity = 0
if "rounds" not in st.session_state:
    st.session_state.rounds = 0
if "alive" not in st.session_state:
    st.session_state.alive = False
if "started" not in st.session_state:
    st.session_state.started = False
if "message_log" not in st.session_state:
    st.session_state.message_log = []


# =========================
# 🧩 Helper: Typewriter Effect
# =========================
def typewriter(text, delay=0.02):
    placeholder = st.empty()
    typed = ""
    for ch in text:
        typed += ch
        placeholder.markdown(f"<p class='text'>{typed}<span class='blink'>█</span></p>", unsafe_allow_html=True)
        time.sleep(delay)
    placeholder.markdown(f"<p class='text'>{typed}</p>", unsafe_allow_html=True)
    st.session_state.message_log.append(text)


# =========================
# 🧮 Gameplay Logic
# =========================
def queue_phase():
    arrivals = np.random.poisson(lam=st.session_state.lmbd)
    waiting_time = random.expovariate(1 / st.session_state.mu)
    typewriter(f"> New subjects arriving... {arrivals} joined the queue.")
    typewriter(f"> Estimated waiting time: {waiting_time:.2f} units.")
    if arrivals > st.session_state.mu:
        typewriter("> λ > μ — The queue is unstable. System under stress.")
    else:
        typewriter("> System stable... for now.")
    st.session_state.toxicity += np.random.poisson(4)
    time.sleep(0.5)


def roulette_phase():
    typewriter("\n> The revolver is placed before you.")
    typewriter("> 6 chambers. 1 bullet.")
    choice = st.radio("Do you spin the chamber?", ["Spin (Independent event)", "Don’t spin (Dependent event)"], key=f"choice_{st.session_state.rounds}")
    if st.button("Pull the trigger ⚙️", key=f"trigger_{st.session_state.rounds}"):
        bullet = random.randint(1, 6)
        spin = random.randint(1, 6) if "Spin" in choice else 1
        if bullet == spin:
            typewriter("💥 Bang. Experiment terminated.")
            st.session_state.alive = False
        else:
            typewriter("Click. Empty chamber. You live another round.")
            antidote_gain = np.random.poisson(2)
            st.session_state.toxicity = max(0, st.session_state.toxicity - antidote_gain)
            typewriter(f"> You gained {antidote_gain}% antidote.")
            st.session_state.rounds += 1
            st.rerun()


def poison_phase():
    drops = np.random.poisson(1)
    if drops > 0:
        st.session_state.toxicity += drops * 8
        typewriter(f"> {drops} drops of toxin leaked. Toxicity +{drops*8}%.")
    else:
        typewriter("> No new leaks detected.")
    time.sleep(0.5)


def report_phase():
    survival_prob = max(0, 1 - (st.session_state.toxicity / 120))
    queue_length = np.random.poisson(3)
    typewriter("\n--- ROUND SUMMARY ---")
    typewriter(f"Rounds Survived: {st.session_state.rounds}")
    typewriter(f"Current Toxicity: {st.session_state.toxicity}%")
    typewriter(f"Expected Queue Length: {queue_length}")
    typewriter(f"λ = {st.session_state.lmbd}   μ = {st.session_state.mu}")
    typewriter(f"Survival Probability: {survival_prob:.2f}")
    typewriter("----------------------")

    if st.session_state.toxicity >= 100:
        typewriter("☠ Toxicity overload. System failure.")
        st.session_state.alive = False


# =========================
# 🚀 Main Game Loop
# =========================
st.markdown("<h1 class='title'>λ: THE LAST QUEUE</h1>", unsafe_allow_html=True)

if not st.session_state.started:
    if st.button("BEGIN EXPERIMENT 🧪"):
        st.session_state.started = True
        st.session_state.alive = True
        st.rerun()
else:
    if st.session_state.alive:
        typewriter("WELCOME, SUBJECT #417.")
        queue_phase()
        poison_phase()
        roulette_phase()
        if st.session_state.alive:
            report_phase()
    else:
        typewriter("EXPERIMENT OVER.")
        typewriter(f"Final Rounds Survived: {st.session_state.rounds}")
        if st.button("Restart"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

