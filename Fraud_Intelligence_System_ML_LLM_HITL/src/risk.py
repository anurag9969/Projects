import numpy as np

def hybrid_risk_score(xgb_probs, anomaly_scores, alpha=0.7):
    """
    Combine supervised probability + anomaly score
    """
    # Normalize anomaly scores (lower = more risky)
    anomaly_norm = (anomaly_scores.max() - anomaly_scores) / (
        anomaly_scores.max() - anomaly_scores.min()
    )

    risk_scores = alpha * xgb_probs + (1 - alpha) * anomaly_norm
    return risk_scores
