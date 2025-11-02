# app.py
import streamlit as st
import time
import random
import numpy as np
import math

# ---------------- Page config & css ----------------
st.set_page_config(page_title="λ: The Last Queue", page_icon="🧪", layout="centered")
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap" rel="stylesheet">
<style>
body { background-color: #07130f; color: #9be39b; font-family: 'Press Start 2P', monospace; }
.title { font-size:20px; text-align:center; margin-top:12px; color:#9be39b; }
.game-text{ font-size:13px; width:78%; margin: 12px auto; text-align:left; white-space:pre-wrap; }
.toxbar { font-family: 'Courier New', monospace; font-size:13px; color:#9be39b; text-align:left; width:78%; margin:6px auto; }
.button { font-family: 'Press Start 2P', monospace; }
.small { font-size:11px; color:#b9f0b9; }
.hr { border-top: 1px dashed #154b3f; margin: 10px 0; width:78%; margin-left:auto; margin-right:auto; }
.center { text-align:center; }
.cursor { display:inline-block; animation: blink 1s steps(1) infinite; }
@keyframes blink { 50% { opacity: 0; } }
</style>
""", unsafe_allow_html=True)

# ---------------- Helper: typewriter that plays once per key ----------------
def typewriter_once(key, text, speed=0.02):
    """Show text with typewriter effect once per key (stored in session_state)."""
    display_key = f"_displayed_{key}"
    if display_key not in st.session_state:
        st.session_state[display_key] = ""
    if st.session_state.get(display_key, "") != text:
        placeholder = st.empty()
        typed = ""
        for ch in text:
            typed += ch
            placeholder.markdown(f"<div class='game-text'>{typed}<span class='cursor'>█</span></div>", unsafe_allow_html=True)
            time.sleep(speed)
        st.session_state[display_key] = text
    else:
        st.markdown(f"<div class='game-text'>{st.session_state[display_key]}</div>", unsafe_allow_html=True)

# ---------------- Toxicity bar ----------------
def toxicity_bar(tox):
    tox = max(0, min(100, tox))
    total_blocks = 20
    filled = int(round((tox / 100) * total_blocks))
    bar = "█" * filled + "░" * (total_blocks - filled)
    if tox >= 85:
        status = "CRITICAL"
    elif tox >= 50:
        status = "HIGH"
    elif tox >= 25:
        status = "WARN"
    else:
        status = "STABLE"
    return f"Toxicity: [{bar}] {tox:.0f}%    STATUS: {status}"

# ---------------- ASCII BANG animation ----------------
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

# ---------------- Session state initialization ----------------
def init_state():
    if "phase" not in st.session_state:
        st.session_state.phase = "tutorial"  # tutorial, playing, ending
    if "tutorial_step" not in st.session_state:
        st.session_state.tutorial_step = 0
    if "tutorial_finished" not in st.session_state:
        st.session_state.tutorial_finished = False
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
        st.session_state.phase_part = "queue"
    if "bullet_pos" not in st.session_state:
        st.session_state.bullet_pos = random.randint(1, 6)
    if "chamber_pointer" not in st.session_state:
        st.session_state.chamber_pointer = 1
    if "ending_type" not in st.session_state:
        st.session_state.ending_type = None
    if "lam_poison" not in st.session_state:
        st.session_state.lam_poison = 0.45
    if "antidote_chance" not in st.session_state:
        st.session_state.antidote_chance = 0.18
    if "displayed_messages" not in st.session_state:
        st.session_state.displayed_messages = set()
    if "_displayed_keys" not in st.session_state:
        st.session_state._displayed_keys = set()

init_state()

# ---------------- Tutorial text (elaborated) ----------------
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

# ---------------- Endings narratives (user-provided exact text) ----------------
ending_texts = {
    "roulette_death": (
        "The revolver hums. The cylinder stops.\n"
        "You hear a sharp click — or was it—\n"
        "BANG.\n"
        "The walls splatter in noise and red logic.\n"
        "Experiment #417: Terminated."
    ),
    "toxic_death": (
        "Your veins pulse neon.\n"
        "You feel numbers crawling under your skin.\n"
        "100% reached.\n"
        "Biological system—irreversible.\n"
        "☠ Simulation Terminated ☠"
    ),
    "queue_collapse": (
        "The hallway grows crowded.\n"
        "Screams echo in infinite recursion.\n"
        "λ ≥ μ.\n"
        "The Lab cannot stabilize its arrivals.\n"
        "System collapses into chaos."
    ),
    "escape": (
        "Dr. Lambda leans forward.\n"
        "For the first time, the screen shows no red.\n"
        "You balanced the rates.\n"
        "Entropy tamed.\n"
        "The Lab of Uncertainty fades away."
    ),
    "secret": (
        "The system no longer tests you.\n"
        "It integrates you.\n"
        "You are no longer Subject #417.\n"
        "You are λ.\n"
        "You are μ.\n"
        "You are balance.\n"
        "> Simulation Complete <"
    ),
    "voluntary_exit": (
        "You close your eyes.\n"
        "Machines hum without you.\n"
        "Somewhere, another subject takes your place.\n"
        "Experiment #418 begins."
    )
}

# ---------------- Utility to trigger endings ----------------
def trigger_ending(kind):
    st.session_state.ending_type = kind
    st.session_state.phase = "ending"
    st.session_state.alive = False

# ---------------- Start a new game ----------------
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
    st.session_state.displayed_messages = set()
    # clear displayed keys
    for k in list(st.session_state.keys()):
        if k.startswith("_displayed_"):
            del st.session_state[k]
    st.rerun()

# ---------------- UI header ----------------
st.markdown(f"<div class='title'>λ: THE LAST QUEUE</div>", unsafe_allow_html=True)
st.markdown("<div class='hr'></div>", unsafe_allow_html=True)

# ---------------- Main states ----------------
if st.session_state.phase == "tutorial":
    idx = st.session_state.tutorial_step
    if idx < len(tutorial_lines):
        key = f"tutorial_{idx}"
        typewriter_once(key, tutorial_lines[idx], speed=0.02)
        
        colA, colB, colC, colD = st.columns([0.8, 1, 0.8, 1])
        with colB:
            if st.button("Next"):
                st.session_state.tutorial_step += 1
                if st.session_state.tutorial_step >= len(tutorial_lines):
                    st.session_state.tutorial_finished = True
                st.rerun()
        with colD:
            if st.button("⏩ Skip Tutorial"):
                st.session_state.tutorial_finished = True
                st.session_state.tutorial_step = len(tutorial_lines)
                st.rerun()
    else:
        st.session_state.tutorial_finished = True

    if st.session_state.tutorial_finished:
        st.markdown("<div class='game-text'>Tutorial complete. Do you accept the experiment?</div>", unsafe_allow_html=True)
        colA, colB, colC = st.columns([1, 2, 1])
        with colB:
            if st.button("▶️ Begin Experiment"):
                start_game()
        with colC:
            if st.button("Decline (Quit)"):
                trigger_ending("voluntary_exit")
                st.rerun()


# ---------------- Playing state ----------------
elif st.session_state.phase == "playing":
    # persistent toxicity meter
    st.markdown(f"<div class='toxbar'>{toxicity_bar(st.session_state.toxicity)}</div>", unsafe_allow_html=True)
    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='game-text'>--- ROUND {st.session_state.round} ---</div>", unsafe_allow_html=True)

    part = st.session_state.phase_part

    # --- QUEUE PHASE ---
    if part == "queue":
        # update params with small drift
        st.session_state.lmbd = round(max(0.2, random.gauss(st.session_state.lmbd, 0.08)), 2)
        st.session_state.mu = round(max(0.5, random.gauss(st.session_state.mu, 0.1)), 2)

        arrivals = np.random.poisson(lam=st.session_state.lmbd)
        services = min(st.session_state.queue_length + arrivals, max(1, np.random.poisson(lam=st.session_state.mu)))
        st.session_state.queue_length = max(0, st.session_state.queue_length + arrivals - services)

        key = f"r{st.session_state.round}_queue"
        s = (
            "[QUEUE PHASE]\n"
            f"New arrivals: {arrivals}\n"
            f"Services processed: {services}\n"
            f"Queue length: {st.session_state.queue_length}\n"
            f"λ = {st.session_state.lmbd}   μ = {st.session_state.mu}"
        )
        typewriter_once(key, s)

        # check collapse
        if st.session_state.lmbd >= st.session_state.mu or st.session_state.queue_length > 12:
            typewriter_once(f"qc_warn_{st.session_state.round}", "\nSYSTEM: λ >= μ — queue instability detected.")
            trigger_ending("queue_collapse")
            st.rerun()

        c1, c2 = st.columns([1, 1])
        with c2:
            if st.button("→ Proceed to Roulette"):
                st.session_state.phase_part = "roulette"
                st.rerun()

    # --- ROULETTE PHASE ---
    elif part == "roulette":
        key = f"r{st.session_state.round}_roulette"
        s = "[ROULETTE PHASE]\nThe revolver is placed before you.\nSix chambers. One bullet."
        typewriter_once(key, s)

        col1, col2, col3 = st.columns([1, 0.6, 1])
        with col1:
            if st.button("Spin (Independent)"):
                chamber = random.randint(1, 6)
                if chamber == st.session_state.bullet_pos:
                    # death
                    typewriter_once(f"bang_{st.session_state.round}_spin", "You spun the cylinder...\nClick... BANG!")
                    ascii_bang()
                    trigger_ending("roulette_death")
                    st.rerun()
                else:
                    typewriter_once(f"safe_{st.session_state.round}_spin", "You spun... click. Empty. You survive this pull.")
                    st.session_state.survival_prob *= (5/6)
                    st.session_state.toxicity = max(0.0, st.session_state.toxicity - 10)
                    st.session_state.chamber_pointer = random.randint(1, 6)
                    st.session_state.phase_part = "poison"
                    st.rerun()

        with col3:
            if st.button("Don't Spin (Dependent)"):
                cp = st.session_state.chamber_pointer
                if cp == st.session_state.bullet_pos:
                    typewriter_once(f"bang_{st.session_state.round}_nospin", "You do not spin...\nClick... BANG!")
                    ascii_bang()
                    trigger_ending("roulette_death")
                    st.rerun()
                else:
                    typewriter_once(f"safe_{st.session_state.round}_nospin", "You don't spin... click. Empty. You live.")
                    st.session_state.survival_prob *= (5/6)
                    st.session_state.toxicity = max(0.0, st.session_state.toxicity - 10)
                    st.session_state.chamber_pointer = (st.session_state.chamber_pointer % 6) + 1
                    st.session_state.phase_part = "poison"
                    st.rerun()

    # --- POISON PHASE ---
    elif part == "poison":
        key = f"r{st.session_state.round}_poison"
        drops = np.random.poisson(lam=st.session_state.lam_poison)
        text = "[POISON PHASE]\n"
        if drops > 0:
            inc = drops * 8
            st.session_state.toxicity = min(100.0, st.session_state.toxicity + inc)
            text += f"{drops} toxin drop(s) leaked. Toxicity +{inc}%.\n"
        else:
            text += "No new leaks detected.\n"
        if random.random() < st.session_state.antidote_chance:
            red = random.randint(5, 15)
            st.session_state.toxicity = max(0.0, st.session_state.toxicity - red)
            text += f"An antidote cart arrives. Toxicity -{red}%.\n"
        text += f"Current toxicity: {st.session_state.toxicity:.1f}%"
        typewriter_once(key, text)

        if st.session_state.toxicity >= 100.0:
            typewriter_once(f"toxic_end_{st.session_state.round}", "\n☠ TOXICITY CRITICAL — SYSTEM FAILURE.")
            trigger_ending("toxic_death")
            st.rerun()

        if st.button("→ View Round Report"):
            st.session_state.phase_part = "report"
            st.rerun()

    # --- REPORT PHASE ---
    elif part == "report":
        rho = st.session_state.lmbd / st.session_state.mu if st.session_state.mu > 0 else 999
        Lq = (rho**2)/(1-rho) if rho < 1 else float('inf')
        key = f"r{st.session_state.round}_report"
        report = (
            f"--- ROUND SUMMARY ---\n"
            f"Rounds Survived: {st.session_state.round}\n"
            f"Current Toxicity: {st.session_state.toxicity:.1f}%\n"
            f"Queue length: {st.session_state.queue_length}\n"
            f"Expected Queue Length (Lq): {Lq if not math.isinf(Lq) else '∞'}\n"
            f"λ = {st.session_state.lmbd:.2f}   μ = {st.session_state.mu:.2f}\n"
            f"Survival Probability (so far): {st.session_state.survival_prob:.3f}\n"
            f"System Stability: {'Stable' if rho < 1 else 'Collapsed'}\n"
            f"----------------------"
        )
        typewriter_once(key, report)

        # check escape / secret endings
        if st.session_state.round >= 10 and rho < 1 and st.session_state.toxicity < 80:
            typewriter_once("escape_trigger", "\nDr. Lambda: 'You have balanced the rates. The experiment concludes.'")
            trigger_ending("escape")
            st.rerun()
        if st.session_state.round >= 20 and st.session_state.survival_prob >= 0.9:
            typewriter_once("secret_trigger", "\nThe console hums. You become the equation.")
            trigger_ending("secret")
            st.rerun()

        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            if st.button("Continue"):
                st.session_state.round += 1
                st.session_state.phase_part = "queue"
                st.session_state.lmbd = min(2.0, round(st.session_state.lmbd + random.uniform(0.02, 0.12), 2))
                st.rerun()
        with c2:
            if st.button("Quit (Voluntary Exit)"):
                trigger_ending("voluntary_exit")
                st.rerun()
        with c3:
            if st.button("Force Status Check"):
                st.rerun()

# ---------------- Ending screens ----------------
elif st.session_state.phase == "ending":
    end = st.session_state.ending_type
    st.markdown("<div class='game-text'>--- EXPERIMENT TERMINATED ---</div>", unsafe_allow_html=True)

    # Use the exact narratives provided by the user
    if end == "roulette_death":
        # show the user-supplied roulette death narrative
        typewriter_once("end_roulette_text", ending_texts["roulette_death"], speed=0.02)
        ascii_bang()
        st.markdown("<div class='game-text'>RESULT: Roulette Death</div>", unsafe_allow_html=True)

    elif end == "toxic_death":
        typewriter_once("end_toxic_text", ending_texts["toxic_death"], speed=0.02)
        st.markdown("<div class='game-text'>RESULT: Toxic Death</div>", unsafe_allow_html=True)

    elif end == "queue_collapse":
        typewriter_once("end_queue_text", ending_texts["queue_collapse"], speed=0.02)
        st.markdown("<div class='game-text'>RESULT: Queue Collapse</div>", unsafe_allow_html=True)

    elif end == "escape":
        typewriter_once("end_escape_text", ending_texts["escape"], speed=0.02)
        st.markdown("<div class='game-text'>RESULT: Escape Ending</div>", unsafe_allow_html=True)

    elif end == "secret":
        typewriter_once("end_secret_text", ending_texts["secret"], speed=0.02)
        st.markdown("<div class='game-text'>RESULT: Secret Transcendence</div>", unsafe_allow_html=True)

    elif end == "voluntary_exit":
        typewriter_once("end_exit_text", ending_texts["voluntary_exit"], speed=0.02)
        st.markdown("<div class='game-text'>RESULT: Voluntary Exit</div>", unsafe_allow_html=True)

    else:
        typewriter_once("end_unknown", "Experiment terminated.", speed=0.02)
        st.markdown("<div class='game-text'>RESULT: Unknown</div>", unsafe_allow_html=True)

    st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='game-text'>Rounds survived: {st.session_state.round}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='toxbar'>{toxicity_bar(st.session_state.toxicity)}</div>", unsafe_allow_html=True)

    if st.button("Restart Game"):
        # clear session and re-init
        keys = list(st.session_state.keys())
        for k in keys:
            del st.session_state[k]
        init_state()
        st.rerun()

# ---------------- Footer ----------------
st.markdown("<div class='hr'></div>", unsafe_allow_html=True)
st.markdown("<div class='small'>Controls: Buttons progress the phases. Tutorial precedes gameplay. All narratives match project spec.</div>", unsafe_allow_html=True)

st.markdown("<div class='small'>Controls: use buttons to progress phases. Text is presented 8-bit style. Tutorial precedes gameplay.</div>", unsafe_allow_html=True)

