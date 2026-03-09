import streamlit as st
import json
import os

from graph import build_guardian_graph
from schemas.decision import DecisionInput
from agents.recommender import recommend_with_fallback
from utils.youtube import search_youtube_semantic


# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="Cognitive Guardian",
    layout="wide",
    initial_sidebar_state="expanded"
)


# -----------------------------
# Memory Store
# -----------------------------
MEMORY_FILE = "user_memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            return json.load(open(MEMORY_FILE, "r"))
        except:
            return {}
    return {}

def save_memory(data):
    json.dump(data, open(MEMORY_FILE, "w"), indent=2)


# -----------------------------
# Language Detection
# -----------------------------
def detect_language(text: str):
    text = text.lower()
    if any(x in text for x in ["hai", "ka", "kya", "nahi"]):
        return "Hindi / Hinglish"
    if any(ord(c) > 128 for c in text):
        return "Non-English"
    return "English"


# -----------------------------
# Emoji Mood Mapper
# -----------------------------
def mood_emoji(score):
    if score >= 75:
        return "😰 High Stress"
    elif score >= 50:
        return "😟 Moderate Stress"
    elif score >= 30:
        return "🙂 Mild Stress"
    return "😌 Calm"


# -----------------------------
# Build Guardian Graph once
# -----------------------------
@st.cache_resource
def load_graph():
    return build_guardian_graph()

guardian_graph = load_graph()


# -----------------------------
# Sidebar UI
# -----------------------------
st.sidebar.title("⚙️ Settings")

domain = st.sidebar.selectbox(
    "Domain",
    ["career", "finance", "education", "personal", "health"]
)

urgency = st.sidebar.slider("Urgency", 1, 5, 3)
reversibility = st.sidebar.slider("Reversibility", 1, 5, 3)

hobby = st.sidebar.text_input("Hobby (optional)")

feedback = st.sidebar.radio(
    "Was this helpful?",
    ["Not selected", "👍 Helpful", "👎 Not Helpful"]
)


# -----------------------------
# Main UI
# -----------------------------
st.title("🧠 Cognitive Guardian")
st.caption("Human-centered AI for emotional clarity and safer decision making.")

decision_text = st.text_area(
    "Describe your situation",
    height=120,
    placeholder="Explain what you are going through or deciding..."
)

analyze_btn = st.button("🚀 Analyze")


# -----------------------------
# Analyze Logic
# -----------------------------
if analyze_btn and decision_text.strip():

    # -----------------------------
    # Load memory
    # -----------------------------
    memory = load_memory()

    if hobby:
        memory["last_hobby"] = hobby

    language = detect_language(decision_text)
    memory["last_language"] = language

    if feedback != "Not selected":
        memory["last_feedback"] = feedback

    save_memory(memory)

    # -----------------------------
    # Guardian Analysis
    # -----------------------------
    decision = DecisionInput(
        decision_text=decision_text,
        urgency=int(urgency),
        reversibility=int(reversibility),
        domain=domain,
    )

    final_state = guardian_graph.invoke({"decision": decision})

    listener = final_state.get("listener_output", {})
    scoring = final_state.get("scoring_output", {})
    verdict = final_state.get("verdict", {})

    pressure = listener.get("pressure_score", 0)
    risk = scoring.get("overall_risk", 0)

    mood = mood_emoji(pressure)

    # -----------------------------
    # Recommendations
    # -----------------------------
    reco = recommend_with_fallback(text=decision_text, hobby=hobby)

    # -----------------------------
    # YouTube Searches
    # -----------------------------
    problem_videos = search_youtube_semantic(
        reco["youtube_primary_query"], max_results=5
    )

    hobby_videos = []
    if reco.get("youtube_hobby_query"):
        hobby_videos = search_youtube_semantic(
            reco["youtube_hobby_query"], max_results=5
        )

    # -----------------------------
    # Layout
    # -----------------------------
    col1, col2 = st.columns(2)

    # -----------------------------
    # Column 1 — Cognitive Analysis
    # -----------------------------
    with col1:
        st.subheader("🧠 Understanding Your Situation")

        st.markdown(f"""
        **You wrote:**  
        > {decision_text}

        **Detected Language:** {language}  
        **Emotional Tone:** {mood}  

        **Verdict:** `{verdict.get("verdict")}`  

        {verdict.get("advice")}
        """)

        st.markdown("### 📊 Confidence Meters")

        st.metric("Pressure", f"{pressure}/100")
        st.progress(pressure / 100)

        st.metric("Overall Risk", f"{risk}/100")
        st.progress(risk / 100)

    # -----------------------------
    # Column 2 — Support & Guidance
    # -----------------------------
    with col2:
        st.subheader("🌿 Personalized Guidance")

        st.markdown(f"""
        **Emotional Insight**  
        {reco.get("emotional_summary")}

        **Why this matters**  
        {reco.get("support_message")}

        **Small steps you can try**
        - 🎬 {reco.get("movie_recommendation")}
        - 🎵 {reco.get("song_recommendation")}
        - 🧘 {reco.get("activity_recommendation")}
        """)

    # -----------------------------
    # YouTube Sections
    # -----------------------------
    st.divider()
    st.subheader("🎯 Videos for Your Problem")

    for v in problem_videos:
        st.markdown(f"- [{v['title']}]({v['url']}) — **{v['match_percent']}% match**")

    if hobby_videos:
        st.subheader("🎨 Videos Related to Your Hobby")
        for v in hobby_videos:
            st.markdown(f"- [{v['title']}]({v['url']}) — **{v['match_percent']}% match**")

    # -----------------------------
    # Memory Snapshot
    # -----------------------------
    st.divider()
    st.subheader("🧠 Your Personal Memory")

    st.json({
        "last_hobby": memory.get("last_hobby"),
        "preferred_language": memory.get("last_language"),
        "last_feedback": memory.get("last_feedback"),
    })


else:
    st.info("✍️ Enter your situation and click **Analyze** to begin.")
