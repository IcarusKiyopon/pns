import streamlit as st
import time

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="λ: The Last Queue", page_icon="🧪", layout="centered")

# ---------- BASIC STYLE ----------
st.markdown("""
    <style>
    body {
        background-color: #0c0f0c;
        color: #90ee90;
        font-family: 'Press Start 2P', monospace;
        text-align: center;
    }
    .title {
        font-size: 22px;
        color: #90ee90;
        margin-top: 40px;
    }
    .game-text {
        font-size: 14px;
        line-height: 1.6;
        white-space: pre-wrap;
        text-align: left;
        margin: 30px auto;
        width: 80%;
    }
    .stButton>button {
        background-color: #222;
        color: #90ee90;
        border: 1px solid #90ee90;
        font-family: 'Press Start 2P', monospace;
        font-size: 12px;
        padding: 8px 20px;
        border-radius: 4px;
    }
    .stButton>button:hover {
        background-color: #90ee90;
        color: #000;
    }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# ---------- TYPEWRITER FUNCTION ----------
def typewriter_effect(text, speed=0.025):
    placeholder = st.empty()
    typed = ""
    for char in text:
        typed += char
        placeholder.markdown(f"<div class='game-text'>{typed}</div>", unsafe_allow_html=True)
        time.sleep(speed)
    return text

# ---------- ELABORATED INTRO STORY ----------
intro_lines = [
    "SYSTEM BOOTING...",
    "ACCESS GRANTED.",
    "WELCOME, SUBJECT #417.",
    "YOU HAVE ENTERED: THE LAB OF UNCERTAINTY.",
    "PLEASE REMAIN CALM.",
    "YOUR BODY CONTAINS A CONTROLLED TOXIN—CODE NAME: LAMBDA SERUM.",
    "THE ANTIDOTE IS UNSTABLE, DISTRIBUTED BY CHANCE.",
    "TO SURVIVE, YOU MUST PLAY A GAME OF ORDER AND CHAOS.",
    "",
    "EVERY TURN, YOU FACE THREE PHASES:",
    "",
    "[1] THE QUEUE PHASE — THE WAIT.",
    " Subjects arrive randomly, like raindrops in an endless storm.",
    " λ (lambda) = ARRIVAL RATE.",
    " μ (mu) = SERVICE RATE.",
    " When λ > μ, the system collapses... too many subjects, too little time.",
    " Patience has a cost. The longer you wait, the more the poison seeps in.",
    "",
    "[2] THE ROULETTE PHASE — THE TEST.",
    " The revolver is placed before you.",
    " Six chambers. One bullet.",
    " Spin, or not?",
    " Spin: the event resets — probability = 1/6.",
    " Don’t spin: the chamber continues — probability shifts as rounds pass.",
    " A true Bernoulli trial, measured in courage.",
    "",
    "[3] THE POISON PHASE — THE DRIFT.",
    " Toxicity rises with time, modeled as a Poisson(λₚ) process.",
    " You may find antidotes… or not.",
    " Antidotes reduce toxicity by random discrete amounts.",
    "",
    "BETWEEN EACH ROUND, DR. LAMBDA WILL REPORT:",
    " • Rounds Survived",
    " • Current Toxicity (%)",
    " • System Stability (λ vs μ)",
    " • Estimated Survival Probability",
    "",
    "IF YOUR TOXICITY REACHES 100% — YOU DIE.",
    "IF THE QUEUE COLLAPSES — YOU DIE.",
    "IF THE REVOLVER FIRES — YOU DIE.",
    "",
    "THE ONLY WAY TO 'WIN'...",
    "...IS TO OUTLAST ENTROPY.",
    "",
    "READY YOUR MIND, SUBJECT #417.",
    "THE EXPERIMENT BEGINS NOW."
]

# ---------- SESSION STATE SETUP ----------
if "step" not in st.session_state:
    st.session_state.step = 0
if "finished_intro" not in st.session_state:
    st.session_state.finished_intro = False
if "displayed_text" not in st.session_state:
    st.session_state.displayed_text = ""

st.markdown("<div class='title'>λ: The Last Queue</div>", unsafe_allow_html=True)

# ---------- MAIN FLOW ----------
if not st.session_state.finished_intro:
    step = st.session_state.step

    if st.session_state.displayed_text != intro_lines[step]:
        st.session_state.displayed_text = typewriter_effect(intro_lines[step])
    else:
        st.markdown(f"<div class='game-text'>{st.session_state.displayed_text}</div>", unsafe_allow_html=True)

    if st.button("Next"):
        st.session_state.step += 1
        if st.session_state.step >= len(intro_lines):
            st.session_state.finished_intro = True
        st.rerun()

else:
    st.success("The experiment awaits. Ready to begin?")
    if st.button("▶️ Start Game"):
        st.session_state.started_game = True
        st.rerun()

if "started_game" in st.session_state and st.session_state.started_game:
    st.markdown("<div class='game-text'>[Game logic will start here soon...]</div>", unsafe_allow_html=True)

