# app.py
import streamlit as st
import time
import random
import numpy as np
import math

# ---------------- Page config & basic style ----------------
st.set_page_config(page_title="λ: The Last Queue", page_icon="🧪", layout="centered")

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
<style>
body { background-color: #07130f; color: #9be39b; font-family: 'Press Start 2P', monospace;}
.title { font-size:20px; text-align:center; margin-top:12px; color:#9be39b;}
.game-text{ font-size:13px; width:78%; margin: 12px auto; text-align:left; white-space:pre-wrap;}
.toxbar { font-family: 'Courier New', monospace; font-size:13px; color:#9be39b; }
.button { font-family: 'Press Start 2P', monospace; }
.small { font-size:11px; color:#b9f0b9; }
.hr { border-top: 1px dashed #154b3f; margin: 10px 0; }
.center { text-align:center; }
</style>
""", unsafe_allow_html=True)

# ---------------- Minimal helper: typewriter that plays once per message ----------------
def typewriter_once(key, text, speed=0.02):
    """
    Shows text with typewriter effect only once per stream_state key.
    key: unique key identifying this message (e.g., f"tutorial_{i}" or f"phase_{round}_{phase}")
    text: string to display
    speed: seconds per char
    Stores final text in session_state[key + "_displayed"].
    """
    disp_key = key + "_displayed"
    if disp_key not in st.session_state:
        st.session_state[disp_key] = ""
    # If not displayed yet, animate and store
    if st.session_state.get(disp_key, "") != text:
        placeholder = st.empty()
        typed = ""
        for ch in text:
            typed += ch
            placeholder.markdown(f"<div class='game-text'>{typed}</div>", unsafe_allow_html=True)
            time.sleep(speed)
        st.session_state[disp_key] = text
    else:
        # already displayed, print instantly
        st.markdown(f"<div class='game-text'>{st.session_state[disp_key]}</div>", unsafe_allow_html=True)

# ---------------- Initialize session state ----------------
def init_state():
    if "phase" not in st.session_state:
        st.session_state.phase = "tutorial"  # tutorial, playing, ending
    if "tutorial_step" not in st.session_state:
        st.session_state.tutorial_step = 0
    if "tutorial_finished" not in st.session_state:
        st.session_state.tutorial_finished = False

    # Gameplay-related (initialized when start game pressed)
    if "game_started" not in st.session_state:
        st.session_state.game_started = False
    if "round" not in st.session_state:
        st.session_state.round = 0
    if "queue_length" not in st.session_state:
        st.session_state.queue_length = 2
    if "toxicity" not in st.session_state:
        st.session_state.toxicity = 15.0
    if "lmbd" not in st.session_state:
        st.session_state.lmbd = 0.8
    if "mu" not in st.session_state:
        st.session_state.mu = 1.1
    if "survival_prob" not in st.session_state:
        st.session_state.survival_prob = 1.0
    if "alive" not in st.session_state:
        st.session_state.alive = True
    if "phase_part" not in st.session_state:
        st.session_state.phase_part = "queue"  # or roulette, poison, report
    if "bullet_pos" not in st.session_state:
        # bullet position fixed at start of game; dependent roulette uses current pointer
        st.session_state.bullet_pos = random.randint(1, 6)
    if "chamber_pointer" not in st.session_state:
        st.session_state.chamber_pointer = 1
    if "ending_type" not in st.session_state:
        st.session_state.ending_type = None
    if "last_message_key" not in st.session_state:
        st.session_state.last_message_key = ""
    if "lam_poison" not in st.session_state:
        st.session_state.lam_poison = 0.45  # average poison drops per round
    if "antidote_chance" not in st.session_state:
        st.session_state.antidote_chance = 0.18  # per round chance
    if "displayed_messages" not in st.session_state:
        st.session_state.displayed_messages = set()

init_state()

# ---------------- Tutorial script (elaborated) ----------------
tutorial_lines = [
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
    "    Subjects arrive randomly. λ = ARRIVAL RATE.",
    "    Services happen at rate μ = SERVICE RATE.",
    "    When λ ≥ μ, the system becomes unstable.",
    "",
    "[2] THE ROULETTE PHASE — THE TEST.",
    "    Six chambers, one bullet. Spin or don't spin.",
    "    Spin: independent 1/6 chance. Don't spin: dependent.",
    "",
    "[3] THE POISON PHASE — THE DRIFT.",
    "    Toxin leaks randomly (Poisson). Antidotes appear sometimes.",
    "",
    "AFTER EACH ROUND, DR. LAMBDA REPORTS:",
    "    • Rounds Survived",
    "    • Current Toxicity (%)",
    "    • λ and μ",
    "    • Survival Probability",
    "",
    "IF TOXICITY ≥ 100% → TOXIC DEATH.",
    "IF λ ≥ μ → QUEUE COLLAPSE.",
    "IF REVOLVER FIRES → ROULETTE DEATH.",
    "",
    "YOU CAN QUIT AFTER ANY REPORT (Voluntary Exit).",
    "THE ONLY WAY TO 'WIN' IS TO OUTLAST ENTROPY.",
    "",
    "THIS IS YOUR WARNING. PREPARE.",
    "THE EXPERIMENT BEGINS NOW."
]

# ---------------- Utility: toxicity bar ascii ----------------
def toxicity_bar(tox):
    tox = max(0, min(100, tox))
    total_blocks = 20
    filled = int(round((tox / 100) * total_blocks))
    bar = "█" * filled + "░" * (total_blocks - filled)
    status = "STABLE"
    if tox >= 85:
        status = "CRITICAL"
    elif tox >= 50:
        status = "HIGH"
    elif tox >= 25:
        status = "WARN"
    return f"Toxicity: [{bar}] {tox:.0f}%    STATUS: {status}"

# ---------------- ASCII gun BANG "animation" ----------------
def ascii_bang():
    frames = [
        "     🔫\n     |===>\n     |\n",
        "     🔫\n     |=====>\n     |\n",
        "     🔫\n     |=======>\n     |\n",
        "     🔫\n     |===>   B A N G !\n     |\n"
    ]
    placeholder = st.empty()
    for f in frames:
        placeholder.markdown(f"<div class='game-text'>{f}</div>", unsafe_allow_html=True)
        time.sleep(0.12)
    time.sleep(0.08)
    placeholder.empty()

# ---------------- Helpers to trigger endings ----------------
def trigger_ending(kind):
    st.session_state.ending_type = kind
    st.session_state.phase = "ending"
    st.session_state.alive = False

# ---------------- Start Game initializer ----------------
def start_game():
    st.session_state.game_started = True
    st.session_state.phase = "playing"
    st.session_state.round = 1
    st.session_state.queue_length = 2
    st.session_state.toxicity = 15.0
    st.session_state.lmbd = round(max(0.3, random.gauss(0.8, 0.12)), 2)
    st.session_state.mu = round(max(0.6, random.gauss(1.1, 0.15)), 2)
    st.session_state.survival_prob = 1.0
    st.session_state.alive = True
    st.session_state.phase_part = "queue"
    st.session_state.bullet_pos = random.randint(1, 6)
    st.session_state.chamber_pointer = 1
    # clear displayed message cache for game
    st.session_state.displayed_messages = set()
    st.rerun()

# ---------------- UI header ----------------
st.markdown(f"<div class='title'>λ: THE LAST QUEUE</div>", unsafe_allow_html=True)
st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

# ---------------- Render tutorial or game depending on state ----------------
if st.session_state.phase == "tutorial":
    # show tutorial step with typewriter_once
    idx = st.session_state.tutorial_step
    if idx < len(tutorial_lines):
        key = f"tutorial_{idx}"
        typewriter_once(key, tutorial_lines[idx], speed=0.02)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("Next"):
                st.session_state.tutorial_step += 1
                if st.session_state.tutorial_step >= len(tutorial_lines):
                    st.session_state.tutorial_finished = True
                st.rerun()
    else:
        st.session_state.tutorial_finished = True

    if st.session_state.tutorial_finished:
        st.markdown("<div class='game-text'>Tutorial complete. Do you accept the experiment?</div>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1])
        with c2:
            if st.button("▶️ Begin Experiment"):
                start_game()
        # allow quit even before starting
        with c3:
            if st.button("Decline (Quit)"):
                trigger_ending("voluntary_exit")
                st.rerun()

# ---------------- Game playing state ----------------
elif st.session_state.phase == "playing":
    # persistent toxicity meter at top
    st.markdown(f"<div class='toxbar'>{toxicity_bar(st.session_state.toxicity)}</div>", unsafe_allow_html=True)
    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

    # Show current round header
    st.markdown(f"<div class='game-text'>--- ROUND {st.session_state.round} ---</div>", unsafe_allow_html=True)

    # Which sub-phase we are in?
    part = st.session_state.phase_part

    # ---------- QUEUE PHASE ----------
    if part == "queue":
        # update lambda and mu slightly (simulate environment variance)
        st.session_state.lmbd = round(max(0.2, random.gauss(st.session_state.lmbd, 0.08)), 2)
        st.session_state.mu = round(max(0.5, random.gauss(st.session_state.mu, 0.1)), 2)

        # arrivals from Poisson(λ)
        arrivals = np.random.poisson(lam=st.session_state.lmbd)
        # services: we approximate with Poisson(mu) but ensure at least 1 chance
        services = min(st.session_state.queue_length + arrivals, max(1, np.random.poisson(lam=st.session_state.mu)))

        st.session_state.queue_length = max(0, st.session_state.queue_length + arrivals - services)

        # show narrative
        key = f"round{st.session_state.round}_queue"
        s = f"[QUEUE PHASE]\nNew arrivals: {arrivals}\nServices processed: {services}\nQueue length: {st.session_state.queue_length}\nλ = {st.session_state.lmbd}   μ = {st.session_state.mu}"
        typewriter_once(key, s)

        # check immediate collapse (if lambda >= mu or queue too long)
        if st.session_state.lmbd >= st.session_state.mu or st.session_state.queue_length > 12:
            # queue collapse ending
            typewriter_once(f"qc_final_{st.session_state.round}", "\nSYSTEM: λ >= μ — queue instability detected.")
            trigger_ending("queue_collapse")
            st.rerun()

        # go to next sub-phase controlled by button
        colA, colB = st.columns([1, 1])
        with colB:
            if st.button("→ Proceed to Roulette"):
                st.session_state.phase_part = "roulette"
                # store last gun state display keys reset for typewriter
                st.rerun()

    # ---------- ROULETTE PHASE ----------
    elif part == "roulette":
        key = f"round{st.session_state.round}_roulette"
        s = "[ROULETTE PHASE]\nThe revolver is placed before you.\nSix chambers. One bullet."
        typewriter_once(key, s)

        # present choice: Spin or Don't Spin
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("Spin (Independent)"):
                # independent: random chamber chosen
                chamber = random.randint(1, 6)
                # bullet_pos is fixed for the current cylinder; compare
                if chamber == st.session_state.bullet_pos:
                    # death
                    typewriter_once(f"bang_{st.session_state.round}_spin", "You spun the cylinder...\nClick... BANG!")
                    ascii_bang()
                    trigger_ending("roulette_death")
                    st.rerun()
                else:
                    typewriter_once(f"safe_{st.session_state.round}_spin", "You spun... click. Empty. You survive this pull.")
                    # survival effects
                    st.session_state.survival_prob *= (5/6)
                    # reward: small antidote dose
                    st.session_state.toxicity = max(0.0, st.session_state.toxicity - 10)
                    # advance chamber pointer randomly (spin resets pointer)
                    st.session_state.chamber_pointer = random.randint(1, 6)
                    # proceed to poison phase
                    st.session_state.phase_part = "poison"
                    st.rerun()

        with col2:
            st.markdown("<div class='small'>OR</div>", unsafe_allow_html=True)

        with col3:
            if st.button("Don't Spin (Dependent)"):
                # dependent: fire current chamber pointer against bullet_pos
                cp = st.session_state.chamber_pointer
                if cp == st.session_state.bullet_pos:
                    # bullet fires
                    typewriter_once(f"bang_{st.session_state.round}_nospin", "You do not spin...\nClick... BANG!")
                    ascii_bang()
                    trigger_ending("roulette_death")
                    st.rerun()
                else:
                    typewriter_once(f"safe_{st.session_state.round}_nospin", "You don't spin... click. Empty. You live.")
                    st.session_state.survival_prob *= (5/6)  # approximate surviving this round
                    st.session_state.toxicity = max(0.0, st.session_state.toxicity - 10)
                    # advance the chamber pointer by 1 (next round will be next chamber if don't spin again)
                    st.session_state.chamber_pointer = (st.session_state.chamber_pointer % 6) + 1
                    # proceed to poison phase
                    st.session_state.phase_part = "poison"
                    st.rerun()

        # also allow voluntary to step back to queue? no — keep strict flow

    # ---------- POISON PHASE ----------
    elif part == "poison":
        key = f"round{st.session_state.round}_poison"
        drops = np.random.poisson(lam=st.session_state.lam_poison)
        text = "[POISON PHASE]\n"
        if drops > 0:
            inc = drops * 8
            st.session_state.toxicity = min(100.0, st.session_state.toxicity + inc)
            text += f"{drops} toxin drop(s) leaked. Toxicity +{inc}%.\n"
        else:
            text += "No new leaks detected.\n"
        # Antidote arrival
        if random.random() < st.session_state.antidote_chance:
            # antidote reduces toxicity by 5-15%
            red = random.randint(5, 15)
            st.session_state.toxicity = max(0.0, st.session_state.toxicity - red)
            text += f"An antidote cart arrives. Toxicity -{red}%.\n"
        text += f"Current toxicity: {st.session_state.toxicity:.1f}%"
        typewriter_once(key, text)

        # check toxic death
        if st.session_state.toxicity >= 100.0:
            typewriter_once(f"toxic_final_{st.session_state.round}", "\n☠ TOXICITY CRITICAL — SYSTEM FAILURE.")
            trigger_ending("toxic_death")
            st.rerun()

        # proceed to report via button
        if st.button("→ View Round Report"):
            st.session_state.phase_part = "report"
            st.rerun()

    # ---------- REPORT PHASE ----------
    elif part == "report":
        # compute simple queue metrics
        rho = st.session_state.lmbd / st.session_state.mu if st.session_state.mu > 0 else 999
        if rho < 1:
            try:
                Lq = (rho**2) / (1 - rho)
            except Exception:
                Lq = float('nan')
        else:
            Lq = float('inf')

        key = f"round{st.session_state.round}_report"
        report = (
            f"--- ROUND SUMMARY ---\n"
            f"Rounds Survived: {st.session_state.round}\n"
            f"Current Toxicity: {st.session_state.toxicity:.1f}%\n"
            f"Queue length: {st.session_state.queue_length}\n"
            f"Expected Queue Length (Lq): {Lq if (not math.isinf(Lq)) else '∞'}\n"
            f"λ = {st.session_state.lmbd:.2f}   μ = {st.session_state.mu:.2f}\n"
            f"Survival Probability (so far): {st.session_state.survival_prob:.3f}\n"
            f"System Stability: {'Stable' if rho < 1 else 'Collapsed'}\n"
            f"----------------------"
        )
        typewriter_once(key, report)

        # Check major-end conditions (escape/secret)
        if st.session_state.round >= 10 and rho < 1 and st.session_state.toxicity < 80:
            # Escape ending
            typewriter_once("escape_hint", "\nDr. Lambda: 'You have balanced the rates. The experiment concludes.'")
            trigger_ending("escape")
            st.rerun()
        if st.session_state.round >= 20 and st.session_state.survival_prob >= 0.9:
            typewriter_once("secret_hint", "\nThe console hums. You become the equation.")
            trigger_ending("secret")
            st.rerun()

        # After report, allow player to continue or quit
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            if st.button("Continue"):
                st.session_state.round += 1
                st.session_state.phase_part = "queue"
                # small environment drift: slightly increase lambda on average
                st.session_state.lmbd = min(2.0, round(st.session_state.lmbd + random.uniform(0.02, 0.12), 2))
                st.rerun()
        with c2:
            if st.button("Quit (Voluntary Exit)"):
                trigger_ending("voluntary_exit")
                st.rerun()
        with c3:
            if st.button("Force Status Check (no-op)"):
                # useful for testers to re-render
                st.rerun()

# ---------------- Ending screen ----------------
elif st.session_state.phase == "ending":
    # small visual header
    end = st.session_state.ending_type
    st.markdown("<div class='game-text'>--- EXPERIMENT TERMINATED ---</div>", unsafe_allow_html=True)

    if end == "roulette_death":
        typewriter_once("end_roulette", "BANG.\nThe chamber fired. The experiment ends here.")
        ascii_bang()
        st.markdown("<div class='game-text'>RESULT: Roulette Death</div>", unsafe_allow_html=True)
    elif end == "toxic_death":
        typewriter_once("end_toxic", "Toxicity reached 100%.\nYour cells fail as numbers climb.")
        st.markdown("<div class='game-text'>RESULT: Toxic Death</div>", unsafe_allow_html=True)
    elif end == "queue_collapse":
        typewriter_once("end_queue", "λ >= μ. The queue swells into a screaming mass.\nSystem collapse is total.")
        st.markdown("<div class='game-text'>RESULT: Queue Collapse</div>", unsafe_allow_html=True)
    elif end == "escape":
        typewriter_once("end_escape", "You balanced λ and μ.\nDr. Lambda nods. You have beaten the process.")
        st.markdown("<div class='game-text'>RESULT: Escape Ending</div>", unsafe_allow_html=True)
    elif end == "secret":
        typewriter_once("end_secret", "You are no longer a subject.\nYou become the process. λ = μ = you.")
        st.markdown("<div class='game-text'>RESULT: Secret Transcendence</div>", unsafe_allow_html=True)
    elif end == "voluntary_exit":
        typewriter_once("end_voluntary", "You decline. Machines hum. Another subject is chosen.")
        st.markdown("<div class='game-text'>RESULT: Voluntary Exit</div>", unsafe_allow_html=True)
    else:
        typewriter_once("end_generic", "Experiment terminated.")
        st.markdown("<div class='game-text'>RESULT: Unknown</div>", unsafe_allow_html=True)

    # final metrics
    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='game-text'>Rounds survived: {st.session_state.round}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='toxbar'>{toxicity_bar(st.session_state.toxicity)}</div>", unsafe_allow_html=True)

    # restart button
    if st.button("Restart Game"):
        # clear session state keys to restart cleanly
        keys = list(st.session_state.keys())
        for k in keys:
            del st.session_state[k]
        # re-init defaults
        init_state()
        st.rerun()

# ---------------- Footer small help ----------------
st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
st.markdown("<div class='small'>Controls: use buttons to progress phases. Text is presented 8-bit style. Tutorial precedes gameplay.</div>", unsafe_allow_html=True)

