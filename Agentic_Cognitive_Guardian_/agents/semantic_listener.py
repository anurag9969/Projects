import re
from agents.llm_client import call_llm

print("🧠 Semantic listener using OpenAI OSS model")

# =====================================================
# 1. OPTIONAL LIGHTWEIGHT SEMANTIC TAGGER
# =====================================================

SEMANTIC_TAGGER_PROMPT = """
You analyze a human decision for cognitive and emotional signals.

Return JSON only:

{
  "inferred_domain": string,
  "emotional_intensity": number between 0 and 1,
  "impulsiveness": number between 0 and 1,
  "uncertainty": number between 0 and 1,
  "risk_summary": string
}
"""


def semantic_analyze(text: str) -> dict:
    try:
        result = call_llm(
            system_prompt=SEMANTIC_TAGGER_PROMPT,
            user_prompt=text
        )

        if not isinstance(result, dict):
            return {}

        return {
            "inferred_domain": result.get("inferred_domain"),
            "emotional_intensity": float(result.get("emotional_intensity", 0.0)),
            "impulsiveness": float(result.get("impulsiveness", 0.0)),
            "uncertainty": float(result.get("uncertainty", 0.0)),
            "risk_summary": result.get("risk_summary"),
        }

    except Exception as e:
        print("⚠️ Semantic tagger failed:", e)
        return {}


# =====================================================
# 2. MAIN COGNITIVE ANALYSIS (LLM-ONLY)
# =====================================================

BASE_ANALYSIS_PROMPT = """
You are a human-centered cognitive analyst AI.

You MUST return JSON ONLY in the exact format below:

{
  "mood_label": string,
  "pressure_score": number (0-100),
  "risk_score": number (0-100),
  "human_explanation": string,
  "human_advice": string,
  "emotional_summary": string,
  "confidence_level": string,
  "grounding_suggestions": {
        "movie": string,
        "song": string,
        "activity": string
  }
}

Pressure score meaning:
- 10–25 → casual / low emotional load
- 30–45 → mild stress or uncertainty
- 50–65 → moderate ongoing concern
- 70–85 → high emotional strain or worry
- 90–100 → crisis-level distress

Risk score meaning:
- 10–30 → low risk
- 40–60 → moderate caution
- 70–90 → high risk
- 90–100 → critical

Rules:
- Pressure reflects emotional load, fear, rumination, and avoidance.
- Risk reflects likelihood of negative long-term consequences.
- Career, interview gaps, income fear, or long uncertainty should rarely be below pressure 40.
- Avoid unrealistically low scores.
- Explanations must be empathetic, human, and contextual.
- Advice must be practical and grounded.
- Grounding suggestions must vary and be relevant.
"""


def llm_cognitive_analyze(
    text: str,
    persona: str = "🤝 Friend",
    simulation: str | None = None
) -> dict:
    """
    Core cognitive analysis with HARD simulation binding.
    """

    persona_style = {
        "🧑‍🏫 Coach": "Be encouraging, structured, motivating, and growth-focused.",
        "🧠 Therapist": "Be empathetic, validating, calm, and reflective.",
        "🎯 Strict Mentor": "Be direct, honest, realistic, and firm but respectful.",
        "🤝 Friend": "Be warm, casual, understanding, and supportive."
    }.get(persona, "Be supportive and clear.")

    # -----------------------------
    # HARD SIMULATION ENFORCEMENT
    # -----------------------------
    simulation_block = ""
    if simulation:
        simulation_block = f"""
CRITICAL SIMULATION MODE — DO NOT IGNORE:

Assume this scenario is TRUE and has already occurred:
→ {simulation}

MANDATORY RULES:
- Speak in past or comparative tense where appropriate.
- Describe how emotions, confidence, and pressure differ from today.
- Describe what realistic progress or consequences would exist now.
- Compare this scenario to the current situation.
- DO NOT give generic advice like "start by".
- Advice should be scenario-specific, not baseline guidance.
"""

    # -----------------------------
    # SAFE PROMPT COMPOSITION
    # -----------------------------
    system_prompt = (
        BASE_ANALYSIS_PROMPT
        + "\n\nPersona style:\n"
        + persona_style
        + "\n\n"
        + simulation_block
    )

    result = call_llm(
        system_prompt=system_prompt,
        user_prompt=text
    )

    if not isinstance(result, dict):
        return {}

    return result


# =====================================================
# 3. YOUTUBE QUERY REWRITE (CRITICAL)
# =====================================================

QUERY_REWRITE_PROMPT = """
Convert the user's problem into a short, precise YouTube search query.

Rules:
- Output ONLY one line (no JSON).
- Remove emotions and filler words.
- Preserve core intent.
- Make it searchable and concrete.
- No explanations.

Examples:
User: "I can't sleep properly and my mind keeps racing"
Output: how to fall asleep fast racing thoughts

User: "I'm stressed about money and salary is low"
Output: increase income financial stress

User: "I am scared of interviews and haven't given one in years"
Output: overcome interview fear after long gap
"""


def llm_rewrite_query(text: str) -> str:
    raw = call_llm(
        system_prompt=QUERY_REWRITE_PROMPT,
        user_prompt=text
    )

    if isinstance(raw, str):
        q = raw.strip().lower()
        if len(q) >= 5:
            return q

    return clean_query_fallback(text)


def clean_query_fallback(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9 ]", " ", text)
    return " ".join(text.split())[:80]
