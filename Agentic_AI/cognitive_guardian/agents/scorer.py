def score_risk(listener_output, critic_output):
    score = listener_output.get("pressure_score", 0)

    critic_flags = len(critic_output.get("critic_notes", []))
    score += critic_flags * 10

    return {
        "overall_risk": min(score, 100)
    }
