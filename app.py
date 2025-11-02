 import streamlit as st
import random
import math
import time

st.set_page_config(page_title="λ: The Last Queue", page_icon="🔫", layout="centered")

# --- 8-bit CSS + Gun animation ---
st.markdown("""
<style>
@import url('https://fonts.cdnfonts.com/css/press-start-2p');

body {
    background-color: #0b0c10;
    color: #66fcf1;
    font-family: 'Press Start 2P', cursive;
    text-align: center;
}

.stApp {
    background-color: #0b0c10;
}

h1, h2, h3, p {
    color: #66fcf1;
    text-shadow: 0 0 10px #45a29e;
}

button, .stButton>button {
    background-color: #1f2833;
    color: #66fcf1;
    border: 2px solid #45a29e;
    padding: 10px 20px;
    font-family: 'Press Start 2P', cursive;
    font-size: 10px;
    text-transform: uppercase;
}

button:hover {
    background-color: #45a29e;
    color: #0b0c10;
    border-color: #66fcf1;
}

#gun {
  position: relative;
  margin: 40px auto;
  width: 150px;
  height: 60px;
  background: #999;
  border-radius: 6px;
  transform-origin: bottom left;
}

#component-top {
  position: absolute;
  top: 0;
  left: 0;
  width: 120px;
  height: 20px;
  background: #555;
  border-radius: 4px;
}

#shooting {
  position: absolute;
  right: -20px;
  top: 10px;
  width: 30px;
  height: 10px;
  background: orange;
  opacity: 0;
  border-radius: 3px;
}

.shoot-play {
  animation: shake 0.2s linear;
}

.animslider {
  animation: slide 0.2s linear;
}

.flash {
  opacity: 1;
  animation: flashanim 0.1s ease-out;
}

@keyframes shake {
  0% { transform: rotate(0deg); }
  25% { transform: rotate(-3deg); }
  50% { transform: rotate(3deg); }
  75% { transform: rotate(-2deg); }
  100% { transform: rotate(0deg); }
}

@keyframes slide {
  0% { transform: translateX(0px); }
  50% { transform: translateX(10px); }
  100% { transform: translateX(0px); }
}

@keyframes flashanim {
  0% { opacity: 1; }
  100% { opacity: 0; }
}
</style>
""", unsafe_allow_html=True)

# --- HTML structure for gun ---
gun_html = """
<div id="gun">
  <div id="component-top"></div>
  <div id="shooting"></div>
</div>

<button id="shootanim">PULL TRIGGER</button>

<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<script>
$(document).ready(function(){
  $("#shootanim").click(function(){
    $("#gun").addClass("shoot-play");
    $("#component-top").addClass("animslider");
    $("#shooting").addClass("flash");
    setTimeout(function(){
      $("#gun").removeClass("shoot-play");
      $("#component-top").removeClass("animslider");
      $("#shooting").removeClass("flash");
    }, 800);
  });
});
</script>
"""

# --- Game Logic ---
st.title("λ: The Last Queue")

if "round" not in st.session_state:
    st.session_state.round = 1
    st.session_state.alive = True
    st.session_state.lmbd = 2.0  # mean arrival rate
    st.session_state.mu = 3.0    # mean service rate

st.markdown("""
You are a **cybernetic gunman** in a dystopian casino.  
Your fate depends on **queue probabilities** — λ for arrivals, μ for escapes.  
Each shot is a **Poisson event**. Each survival is a service completion.

Pull the trigger. Pray to the laws of probability.
""")

# display gun
st.components.v1.html(gun_html, height=300)

# --- Gameplay mechanics ---
if st.button("Shoot (simulate event)"):
    if st.session_state.alive:
        # simulate arrivals ~ Poisson(λ)
        arrivals = random.poisson(lam=st.session_state.lmbd) if hasattr(random, "poisson") else random.randint(0, 4)
        service_time = random.expovariate(1/st.session_state.mu)
        wait_prob = st.session_state.lmbd / st.session_state.mu

        st.write(f"Round {st.session_state.round}: λ={st.session_state.lmbd}, μ={st.session_state.mu}")
        st.write(f"Incoming queue arrivals: {arrivals}")
        st.write(f"Service time simulated: {service_time:.2f}")
        st.write(f"Queue waiting probability (λ/μ): {wait_prob:.2f}")

        # Determine survival based on λ/μ
        survival_chance = max(0.05, 1 - wait_prob)
        if random.random() < survival_chance:
            st.success("💥 Click! You live. Probability was in your favor.")
            st.session_state.lmbd += 0.3  # increase risk next round
            st.session_state.mu += random.choice([-0.2, 0, 0.2])
        else:
            st.error("☠️ Bang! The queue collapsed. You are statistically dead.")
            st.session_state.alive = False
        st.session_state.round += 1
    else:
        st.warning("The game is over. Restart to face the queue again.")

if st.button("Restart"):
    for key in ["round", "alive", "lmbd", "mu"]:
        st.session_state.pop(key, None)
    st.experimental_rerun()
