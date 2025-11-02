import streamlit as st
import random
import math
import time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="λ: The Last Queue", page_icon="🧪", layout="centered")

# ---------------- CSS STYLING ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

html, body, [class*="css"] {
  font-family: 'Press Start 2P', cursive !important;
  background-color: #0f380f;
  color: #9bbc0f;
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
}
.stButton>button:hover {
  background-color: #8bac0f;
  color: black;
}
.big {font-size: 14px !important; line-height: 1.8;}
.title {font-size: 20px !important;}
.cursor::after {
  content: '_';
  animation: blink 1s step-start infinite;
}
@keyframes blink { 50% {opacity: 0;} }
</style>
""", unsafe_allow_html=True)

# ---------------- TEXT EFFECT ----------------
def type_text(text, delay=0.03):
    """Display text letter by letter for effect."""
    box = st.empty()
    s = ""
    for char in text:
        s += char
        box.markdown(f"<p class='big cursor'>{s}</p>", unsafe_allow_html=True)
        time.sleep(delay)
    time.sleep(0.3)

# ---------------- STATE ----------------
if "round" not in st.session_state:
    st.session_state.round = 1
    st.session_state.toxicity = 20.0
    st.session_state.queue_len = 2
    st.session_state.alive = True
    st.session_state.lmbd = 0.8
    st.session_state.mu = 1.1
    st.session_state.report = ""
    st.session_state.survival_prob = 1.0

# ---------------- TITLE ----------------
st.markdown("<div class='title'>λ : THE LAST QUEUE</div><br>", unsafe_allow_html=True)

# ---------------- GAME LOOP ----------------
if st.session_state.alive:

    # NARRATION
    type_text(f"--- ROUND {st.session_state.round} ---")
    type_text("You wait in the queue...")
    arrivals = random.poisson(lam=st.session_state.lmbd) if hasattr(random, 'poisson') else int(random.expovariate(1/st.session_state.lmbd))
    st.session_state.queue_len += arrivals
    wait = random.expovariate(1/st.session_state.mu)
    type_text(f"> New arrivals: {arrivals}")
    type_text(f"> Estimated wait: {wait:.1f} units")

    # Poison leaks (Poisson)
    poison_drops = random.poisson(lam=0.6) if hasattr(random, 'poisson') else (0 if random.random() < 0.55 else 1)
    if poison_drops > 0:
        gain = poison_drops * 8
        st.session_state.toxicity += gain
        type_text(f"> Poison leak detected. +{gain}% toxicity.")

    # Roulette choice
    type_text("It’s your turn at the roulette.")
    spin = st.radio("Choose:", ["[1] Spin the chamber (independent)", "[2] Don’t spin (dependent)"])
    if st.button("Pull the trigger"):
        bullet = random.randint(1, 6)
        if spin.startswith("[1]"):
            chamber = random.randint(1, 6)
        else:
            chamber = bullet  # depends on prior state, same distribution effectively

        if chamber == 1:
            type_text("💥 The chamber fires. Simulation ends.")
            st.session_state.alive = False
        else:
            type_text("Click. Empty. You live another round.")
            st.session_state.toxicity -= 10
            st.session_state.survival_prob *= (5/6)
            st.session_state.round += 1
            st.session_state.queue_len = max(1, st.session_state.queue_len - 1)

            # Report
            stable = "Stable" if st.session_state.lmbd < st.session_state.mu else "Collapsed"
            st.session_state.report = f"""
--- ROUND SUMMARY ---
Rounds Survived: {st.session_state.round - 1}
Current Toxicity: {min(st.session_state.toxicity, 100):.1f}%
Expected Queue Length: {st.session_state.queue_len:.2f}
λ = {st.session_state.lmbd:.2f}   μ = {st.session_state.mu:.2f}
Survival Probability (so far): {st.session_state.survival_prob:.2f}
System Stability: {stable}
----------------------
"""
            st.rerun()

else:
    # ENDINGS
    if st.session_state.toxicity >= 100:
        end = "☣️ Toxicity overload. System failure."
    elif st.session_state.lmbd >= st.session_state.mu:
        end = "⚠️ Queue overflow. Chaos reigns."
    elif st.session_state.round >= 10 and st.session_state.lmbd < st.session_state.mu:
        end = "🧪 You balanced λ and μ. Dr. Lambda nods. You beat the process."
    else:
        end = "Simulation terminated."
    st.markdown(f"<p class='big'>{end}</p>", unsafe_allow_html=True)
    st.markdown(f"<pre>{st.session_state.report}</pre>", unsafe_allow_html=True)
    if st.button("Restart"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()
