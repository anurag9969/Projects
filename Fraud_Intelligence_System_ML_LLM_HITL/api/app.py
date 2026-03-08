from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np
import joblib

from src.risk import hybrid_risk_score
from src.decision import decision_engine
from src.feedback import init_db, store_feedback

app = FastAPI(title="Fraud Intelligence API")

# Load models
xgb_model = joblib.load("models/xgb.pkl")
iso_model = joblib.load("models/iso.pkl")

# Init DB
init_db()

class Transaction(BaseModel):
    features: list  # length = 30 (Time, V1..V28, Amount)

class Feedback(BaseModel):
    transaction_index: int
    risk_score: float
    model_decision: int
    human_label: int  # 0 or 1

@app.post("/predict")
def predict(tx: Transaction):
    X = np.array(tx.features).reshape(1, -1)

    # Supervised prob
    xgb_prob = xgb_model.predict_proba(X)[:, 1]

    # Anomaly score
    anomaly_score = iso_model.decision_function(X)

    # Hybrid risk
    risk = hybrid_risk_score(xgb_prob, anomaly_score)[0]

    # Decision
    decision = decision_engine(np.array([risk]))[0]

    return {
        "fraud_probability": float(xgb_prob[0]),
        "anomaly_score": float(anomaly_score[0]),
        "risk_score": float(risk),
        "decision": int(decision)  # 0 approve, 1 review, 2 block
    }

@app.post("/feedback")
def feedback(fb: Feedback):
    store_feedback(
        transaction_index=fb.transaction_index,
        model_risk_score=fb.risk_score,
        model_decision=fb.model_decision,
        human_label=fb.human_label
    )
    return {"status": "feedback stored"}
