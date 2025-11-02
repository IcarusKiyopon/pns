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
def typewriter(text, speed=0.02):
    placeholder = st.empty()
    displayed_text = ""
    for char in text:
        displayed_text += char
        placeholder.markdown(f"<div class='game-text'>{displayed_text}</div>", unsafe_allow_html=True)
        time.sleep(speed)

# ---------- TUTORIAL MESSAGES ----------
intro_lines = [
    "WELCOME, SUBJECT #417.",
    "YOU HAVE ENTERED THE LAB OF UNCERTAINTY.",
    "YOUR BODY CONTAINS A SLOW POISON.",
    "ANTIDOTES ARRIVE RANDOMLY.",
    "YOUR LIFE ENDS AT 100% TOXICITY.",
    "TO EARN ANTIDOTES, YOU MUST PLAY THE ROULETTE.",
    "EACH TURN — A TEST OF PROBABILITY.",
    "EACH SECOND — A WAIT IN THE QUEUE.",
    "λ: ARRIVAL RATE. μ: SERVICE RATE.",
    "WHEN λ > μ … SYSTEM COLLAPSES.",
    "THE EXPERIMENT BEGINS."
]

# ---------- STATE HANDLING ----------
if "step" not in st.session_state:
    st.session_state.step = 0
if "finished_intro" not in st.session_state:
    st.session_state.finished_intro = False
if "last_displayed_step" not in st.session_state:
    st.session_state.last_displayed_step = -1

st.markdown("<div class='title'>λ: The Last Queue</div>", unsafe_allow_html=True)

# ---------- MAIN FLOW ----------
if not st.session_state.finished_intro:
    step = st.session_state.step

    # Only play typewriter when a new line is first reached
    if st.session_state.last_displayed_step != step:
        st.session_state.last_displayed_step = step
        typewriter(intro_lines[step])
    else:
        st.markdown(f"<div class='game-text'>{intro_lines[step]}</div>", unsafe_allow_html=True)

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

# ---------- PLACEHOLDER for next phase ----------
if "started_game" in st.session_state and st.session_state.started_game:
    st.markdown("<div class='game-text'>[Game logic will start here soon...]</div>", unsafe_allow_html=True)
