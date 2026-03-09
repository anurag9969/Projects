import re

# ---------------------------
# SIGNAL LEXICONS
# ---------------------------

EMOTIONAL_DISTRESS = [
    "fed up", "done", "angry", "furious", "tired", "exhausted", "burnt out",
    "can't take", "cannot take", "had enough", "sick of", "frustrated",
    "hopeless", "helpless", "worthless", "hate", "depressed", "miserable",
    "crying", "broken", "stressed", "stress", "anxious", "panic", "scared",
    "worried", "terrified", "overwhelmed", "pressure", "mentally tired"
]

SELF_HARM_KEYWORDS = [
    "suicide", "kill myself", "end my life", "die", "want to die",
    "self harm", "cut myself", "jump off", "hang myself",
    "overdose", "poison myself", "no reason to live",
    "better off dead", "can't go on"
]

COGNITIVE_OVERLOAD = [
    "too much", "can't think", "confused", "lost", "no idea", "don't know",
    "everything at once", "mess", "chaos", "nothing working", "stuck",
    "trapped", "no way out", "brain dead", "can't decide"
]

IMPULSIVE_LANGUAGE = [
    "now", "today", "immediately", "right away", "asap", "instantly",
    "this moment", "can't wait", "must do", "have to", "right now"
]

ABSOLUTE_LANGUAGE = [
    "always", "never", "nothing", "everything", "no one", "everyone"
]


# ---------------------------
# HELPER FUNCTIONS
# ---------------------------

def count_hits(text: str, keywords: list[str]) -> int:
    lower = text.lower()
    return sum(1 for k in keywords if k in lower)


# ---------------------------
# PRESSURE SCORING
# ---------------------------

def pressure_score(text, urgency, reversibility):
    score = 0
    lower = text.lower()

    emotional_hits = count_hits(lower, EMOTIONAL_DISTRESS)
    overload_hits = count_hits(lower, COGNITIVE_OVERLOAD)
    impulsive_hits = count_hits(lower, IMPULSIVE_LANGUAGE)
    absolute_hits = count_hits(lower, ABSOLUTE_LANGUAGE)
    self_harm_hits = count_hits(lower, SELF_HARM_KEYWORDS)

    # Linguistic signals
    score += emotional_hits * 8
    score += overload_hits * 8
    score += impulsive_hits * 6
    score += absolute_hits * 4

    # Structural risk
    score += urgency * 10
    score += (6 - reversibility) * 10

    # Intensity patterns
    if re.search(r"!{2,}", text):
        score += 8

    if re.search(r"\b[A-Z]{3,}\b", text):
        score += 5

    # Critical escalation
    if self_harm_hits > 0:
        score += 40

    return min(score, 100), {
        "emotional_hits": emotional_hits,
        "overload_hits": overload_hits,
        "impulsive_hits": impulsive_hits,
        "absolute_hits": absolute_hits,
        "self_harm_hits": self_harm_hits
    }


# ---------------------------
# MAIN ANALYSIS
# ---------------------------

def analyze(text, urgency, reversibility):
    pressure, signals = pressure_score(text, urgency, reversibility)

    # Risk flags for gatekeeper
    risk_flags = []
    if signals["self_harm_hits"] > 0:
        risk_flags.append("self_harm_detected")

    # Verdict logic
    if signals["self_harm_hits"] > 0 or pressure >= 80:
        verdict = "CRITICAL RISK"
        advice = (
            "This sounds very intense and painful. You deserve support and care. "
            "Please consider reaching out to someone you trust or a professional right now."
        )

    elif pressure >= 60:
        verdict = "HIGH RISK"
        advice = (
            "Strong emotional or cognitive pressure detected. "
            "Avoid irreversible actions and slow down decision-making."
        )

    elif pressure >= 35:
        verdict = "MODERATE RISK"
        advice = (
            "Some stress signals detected. Give yourself time and avoid acting impulsively."
        )

    else:
        verdict = "LOW RISK"
        advice = (
            "Your emotional and cognitive signals appear stable."
        )

    return {
        "pressure_score": pressure,     # ✅ fixed key
        "verdict": verdict,
        "advice": advice,
        "signals": signals,
        "risk_flags": risk_flags        # ✅ added
    }


# ---------------------------
# GRAPH ENTRY WRAPPER
# ---------------------------

def analyze_decision(decision):
    """
    Adapter for LangGraph.
    """
    return analyze(
        decision.decision_text,
        decision.urgency,
        decision.reversibility
    )
