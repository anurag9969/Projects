def simulate_future(decision, listener_output):
    pressure = listener_output.get("pressure_score", 0)

    if pressure >= 75:
        return {
            "future_risk": "high",
            "description": "Likely negative consequences, irreversible damage, or regret."
        }

    if pressure >= 40:
        return {
            "future_risk": "medium",
            "description": "Possible setbacks, moderate uncertainty."
        }

    return {
        "future_risk": "low",
        "description": "Low immediate risk, reversible outcome."
    }
