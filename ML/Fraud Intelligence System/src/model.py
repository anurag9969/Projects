import xgboost as xgb
from sklearn.metrics import (
    classification_report,
    precision_recall_curve,
    average_precision_score
)

def train_xgboost(X_train, y_train):
    """
    Trains baseline XGBoost fraud model.
    """

    # Handle class imbalance
    scale_pos_weight = (y_train == 0).sum() / (y_train == 1).sum()

    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos_weight,
        eval_metric="logloss",
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)
    return model


def evaluate_model(model, X_val, y_val):
    """
    Evaluates model using PR-AUC and recall-focused metrics.
    """
    y_prob = model.predict_proba(X_val)[:, 1]
    y_pred = (y_prob >= 0.5).astype(int)

    pr_auc = average_precision_score(y_val, y_prob)

    print("\n--- Classification Report ---")
    print(classification_report(y_val, y_pred, digits=4))

    print(f"PR-AUC: {pr_auc:.4f}")
