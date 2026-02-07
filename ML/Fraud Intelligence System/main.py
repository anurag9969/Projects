from src.data_loader import load_data
from src.preprocessing import clean_data
from src.target_definition import split_features_target
from src.split import train_val_split
from src.model import train_xgboost, evaluate_model
from src.anomaly import train_isolation_forest,anomaly_scores 
from src.explain import explain_model, global_explanation, local_explanation
from src.decision import decision_engine
from src.risk import hybrid_risk_score
import numpy as np 
import os 
import joblib 
from src.feedback import init_db,store_feedback
from src.monitoring import monitor_model

if __name__ == "__main__":

    # Load → clean → split
    df = load_data("data/raw_transactions.csv")
    df_clean = clean_data(df)
    X, y = split_features_target(df_clean)
    X_train, X_val, y_train, y_val = train_val_split(X, y)

    # Supervised Model 
    xgb_model = train_xgboost(X_train,y_train)
    evaluate_model(xgb_model,X_val,y_val)

    # Unsupervised Model 
    iso_model = train_isolation_forest(X_train,y_train)

    # ------------------ Save Models -------------------------------
    os.makedirs("models", exist_ok=True)
    joblib.dump(xgb_model, "models/xgb.pkl")
    joblib.dump(iso_model, "models/iso.pkl")


    val_scores = anomaly_scores(iso_model,X_val)

    # Convert anomaly scores to flags (lower score = more anomalous)
    threshold = np.percentile(val_scores,1) # top 1% most anomalous
    anomaly_flags = (val_scores < threshold).astype(int)

    print("\nAnomaly Detection Summary:")
    print("Total anomalies flagged:",anomaly_flags.sum())

    # ---- SHAP Explainability ----
    X_explain = X_val.sample(300, random_state=42)

    explainer, shap_values = explain_model(xgb_model, X_explain)

    print("\nGlobal SHAP explanation")
    global_explanation(shap_values)

    print("\nLocal SHAP explanation")
    local_explanation(shap_values, index=0)

    # ------------------ Hybrid Risk Scoring -------------------------------
    xgb_probs = xgb_model.predict_proba(X_val)[:, 1]

    risk_scores = hybrid_risk_score(
        xgb_probs=xgb_probs,
        anomaly_scores=val_scores,
        alpha=0.7
    )

    # ------------------ Top Risky Transactions -------------------------------
    top_indices = np.argsort(risk_scores)[-10:][::-1]

    # ------------------ Decision Engine -------------------------------
    decisions = decision_engine(
        risk_scores,
        low_threshold=0.3,
        high_threshold=0.8
    )

    print("\nDecision Summary:")
    print("APPROVE :",(decisions == 0).sum())
    print("REVIEW  :",(decisions == 1).sum())
    print("BLOCK   :",(decisions == 2).sum())

    # -------------------- Human Feedback --------------------------------
    os.makedirs("feedback",exist_ok=True)
    init_db()

    # Simulate analyst feedback for top risky cases 
    print("\nSimulating human feedback .....")

    for idx in top_indices[:3]: # Top 3 risky transactions 
        human_label = int(
                            input(
                                    f"Transaction {idx} | Risk={risk_scores[idx]:.3f} | "
                                    f"Model Decision={decisions[idx]} | Enter human label (0/1): "
                                )
                        )


    store_feedback(
        transaction_index=int(idx),
        model_risk_score=float(risk_scores[idx]),
        model_decision=int(decisions[idx]),
        human_label=human_label
    )

    print("Human feedback stored successfully : ")

    # ------------------ Monitoring -------------------------------
    monitor_model()

