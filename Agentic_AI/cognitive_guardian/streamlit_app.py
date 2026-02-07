import streamlit as st
import os, json, uuid
from datetime import datetime, timezone

from agents.semantic_listener import (
    llm_cognitive_analyze,
    llm_rewrite_query
)

from utils.youtube import search_youtube_semantic

# -------------------------------------------------
# Page Config
# -------------------------------------------------
st.set_page_config(
    page_title="Cognitive Guardian",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------
# Anonymous User ID (No Login)
# -------------------------------------------------
if "anon_id" not in st.session_state:
    st.session_state.anon_id = str(uuid.uuid4())

USER_DIR = "user_memory"
os.makedirs(USER_DIR, exist_ok=True)

def memory_path(uid):
    return os.path.join(USER_DIR, f"{uid}.json")

def load_memory(uid):
    if os.path.exists(memory_path(uid)):
        return json.load(open(memory_path(uid)))
    return {"history": []}

def save_memory(uid, data):
    json.dump(data, open(memory_path(uid), "w"), indent=2)

memory = load_memory(st.session_state.anon_id)

# -------------------------------------------------
# Sidebar Controls
# -------------------------------------------------
st.sidebar.title("🎛 Controls")

persona = st.sidebar.selectbox(
    "Persona (Tone)",
    ["🧑‍🏫 Coach", "🧠 Therapist", "🎯 Strict Mentor", "🤝 Friend"]
)

simulation_choice = st.sidebar.radio(
    "Decision Simulation",
    [
        "If I continue current path",
        "If I wait 3 months",
        "If I had done this 3 months ago"
    ]
)

clear_memory = st.sidebar.button("🧹 Clear My Data")

if clear_memory:
    save_memory(st.session_state.anon_id, {"history": []})
    st.sidebar.success("Memory cleared")

# -------------------------------------------------
# Main UI
# -------------------------------------------------
st.title("🧠 Cognitive Guardian")
st.caption("Human-centered AI for clarity, confidence, and safer decisions.")

decision_text = st.text_area(
    "Describe your situation",
    height=140,
    placeholder="Explain what you’re dealing with honestly…"
)

analyze = st.button("🚀 Analyze")

# -------------------------------------------------
# Analysis
# -------------------------------------------------
if analyze and decision_text.strip():

    # 🧠 LLM Cognitive Analysis (LLM ONLY)
    llm = llm_cognitive_analyze(
        text=decision_text,
        persona=persona,
        simulation=simulation_choice
    )

    # --- Safe extraction ---
    mood = llm.get("mood_label", "🙂 Neutral")
    pressure = int(llm.get("pressure_score", 50))
    risk = int(llm.get("risk_score", 50))

    explanation = llm.get("human_explanation", "")
    advice = llm.get("human_advice", "")
    emotional_summary = llm.get("emotional_summary", "")
    confidence_level = llm.get("confidence_level", "Medium")

    grounding = llm.get("grounding_suggestions", {})
    movie = grounding.get("movie", "A calming movie")
    song = grounding.get("song", "Relaxing music")
    activity = grounding.get("activity", "Take a short mindful break")

    # -------------------------------------------------
    # Micro-Animation Theme Logic
    # -------------------------------------------------
    if pressure < 35:
        theme = "calm"
    elif pressure < 65:
        theme = "neutral"
    else:
        theme = "stress"

    # -------------------------------------------------
    # Store history
    # -------------------------------------------------
    memory["history"].append({
        "time": datetime.now(timezone.utc).isoformat(),
        "pressure": pressure,
        "risk": risk
    })
    memory["history"] = memory["history"][-10:]
    save_memory(st.session_state.anon_id, memory)

    # -------------------------------------------------
    # Dynamic Background / Animation (CSS)
    # -------------------------------------------------
    if theme == "calm":
        bg = "linear-gradient(120deg, #0f2027, #203a43, #2c5364)"
    elif theme == "stress":
        bg = "linear-gradient(120deg, #2c0f0f, #3a2020, #642c2c)"
    else:
        bg = "linear-gradient(120deg, #111827, #1f2933, #020617)"

    st.markdown(
        f"""
        <style>
        .stApp {{
            background: {bg};
            transition: background 2s ease;
        }}
        .pulse {{
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0% {{ box-shadow: 0 0 0px rgba(255,100,100,0.4); }}
            50% {{ box-shadow: 0 0 20px rgba(255,100,100,0.8); }}
            100% {{ box-shadow: 0 0 0px rgba(255,100,100,0.4); }}
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    # -------------------------------------------------
    # Layout
    # -------------------------------------------------
    col1, col2 = st.columns([1.2, 1])

    with col1:
        st.subheader("🧠 Understanding Your Situation")
        st.markdown(f"""
        **Emotional Tone:** {mood}  
        **Persona Used:** {persona}  
        **Simulation:** {simulation_choice}

        ---
        {explanation}
        """)

        st.markdown("### 📊 Confidence Meters")
        st.metric("Pressure", f"{pressure}/100")
        st.progress(pressure / 100)

        st.metric("Overall Risk", f"{risk}/100")
        st.progress(risk / 100)

    with col2:
        st.subheader("🌿 Personalized Guidance")
        st.markdown(advice)

        st.markdown("### 🧾 Session Summary")
        st.info(emotional_summary)

    # -------------------------------------------------
    # YouTube (Problem First)
    # -------------------------------------------------
    st.divider()
    st.subheader("📺 Videos for Your Problem")

    # 🔁 Rewrite long user text into a clean search query
    yt_query = llm_rewrite_query(decision_text)

    # 🎯 Semantic YouTube search
    videos = search_youtube_semantic(yt_query, max_results=5)

    for v in videos:
        c1, c2 = st.columns([1, 3])
        with c1:
            st.image(v["thumbnail"], use_container_width=True)
        with c2:
            st.markdown(f"**{v['title']}**")
            st.write(f"Relevance: {v['match_percent']}%")
            st.markdown(f"[▶ Watch on YouTube]({v['url']})")
        st.divider()

else:
    st.info("✍️ Enter your situation and click **Analyze** to begin.")
