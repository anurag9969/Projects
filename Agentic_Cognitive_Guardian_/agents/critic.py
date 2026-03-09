def critique_decision(decision, listener_output, simulation_output):
    """
    Dict-safe critic agent.
    """

    risks = []

    if isinstance(decision, dict):
        reversibility = int(decision.get("reversibility", 3))
        urgency = int(decision.get("urgency", 3))
    else:
        reversibility = int(decision.reversibility)
        urgency = int(decision.urgency)

    if simulation_output.get("future_risk") == "high":
        risks.append("Simulated future indicates high potential harm.")

    if reversibility <= 2:
        risks.append("This decision may be difficult to reverse once taken.")

    if urgency >= 4:
        risks.append("High urgency may increase impulsive action.")

    if not risks:
        risks.append("No major structural risks detected.")

    return {
        "critic_notes": risks     # ✅ fixed key
    }
