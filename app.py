import streamlit as st
import numpy as np

st.set_page_config(page_title="λ: The Last Queue", page_icon="☣", layout="centered")
st.markdown("<h1 style='text-align:center;'>λ: The Last Queue</h1>", unsafe_allow_html=True)
st.markdown("---")

# Game state
if "stage" not in st.session_state:
    st.session_state.stage = 0

def next_stage():
    st.session_state.stage += 1

stage = st.session_state.stage

if stage == 0:
    st.markdown("You wake up in a concrete room. The PA system hums.")
    st.markdown("> \"Welcome to the Probability Trials.\"")
    if st.button("Enter the queue"):
        next_stage()

elif stage == 1:
    st.subheader("Stage 1: The Queue (M/M/1)")
    λ = st.slider("Arrival Rate (λ)", 1.0, 5.0, 3.0)
    μ = st.slider("Service Rate (μ)", 1.0, 6.0, 5.0)
    if μ <= λ:
        st.error("System unstable (μ must be > λ)")
    else:
        wait_time = 1 / (μ - λ)
        st.write(f"Expected waiting time: *{wait_time:.2f} units*")
        if st.button("Proceed to Poison Chamber"):
            next_stage()

elif stage == 2:
    st.subheader("Stage 2: Poison Chamber (Poisson Process)")
    λ_poison = st.slider("Poison drop rate λ", 0.5, 5.0, 2.0)
    drops = np.random.poisson(λ_poison)
    st.write(f"The chamber dripped *{drops} times*.")
    survival_prob = np.exp(-λ_poison)
    st.write(f"Probability you survive: *{survival_prob:.2f}*")
    if st.button("Proceed to Roulette"):
        st.session_state.survival = survival_prob
        next_stage()

elif stage == 3:
    st.subheader("Stage 3: Roulette (Bernoulli Trial)")
    p = 0.8
    result = np.random.choice(["Click", "Bang"], p=[p, 1 - p])
    st.write(f"The cylinder spins... *{result}!*")
    overall = st.session_state.survival * p
    st.write(f"Overall survival probability: *{overall:.2f}*")
    if st.button("Restart Game"):
        st.session_state.stage = 0
        st.rerun()
