def gate_decision(scoring_output, listener_output=None):

    # 🚨 HARD SAFETY OVERRIDE
    if listener_output and "self_harm_detected" in listener_output.get("risk_flags", []):
        return {
            "verdict": "BLOCK",
            "advice": "You're going through intense thoughts right now. You deserve care, support, and time. Please pause before taking any action.",

            "recommendations": {
                "song": "Fix You – Coldplay",
                "youtube": "Guided Breathing for Anxiety – 5 Minutes (The Honest Guys)",
                "movie": "The Pursuit of Happyness (2006)",
                "activity": "Drink a glass of water, take 5 slow breaths, and step outside for fresh air if possible."
            }
        }

    risk = scoring_output.get("overall_risk", 0)

    if risk >= 80:
        return {
            "verdict": "BLOCK",
            "advice": "High risk detected. Do NOT proceed without expert guidance."
        }

    if risk >= 50:
        return {
            "verdict": "PROCEED_WITH_CAUTION",
            "advice": "Risk is moderate. Consider safeguards and delay irreversible actions."
        }

    return {
        "verdict": "SAFE_TO_PROCEED",
        "advice": "Risk appears low. Proceed carefully."
    }
