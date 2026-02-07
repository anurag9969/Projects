import numpy as np 

def decision_engine(
        risk_scores,
        low_threshold=0.3,
        high_threshold=0.8
):
    """
    Converts risk scores into actions. 

    Returns:
    0 -> APPROVE
    1 -> REVIEW 
    2 -> BLOCK
    """

    decisions = []

    for score in risk_scores: 
        if score >= high_threshold:
            decisions.append(2) # BLOCK
        elif score >= low_threshold:
            decisions.append(1) # REVIEW 
        else:
            decisions.append(0) # APPROVE 
        
    return np.array(decisions)