from sklearn.ensemble import IsolationForest
import numpy as np 

def train_isolation_forest(X_train,y_train):
    """
    Train Isolation Forest on Normal transactions only. 
    """

    # Train Only on non-fraud data 
    X_normal = X_train[y_train == 0]

    model = IsolationForest(
        n_estimators=200,
        contamination=0.002, 
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_normal)
    return model 

def anomaly_scores(model,X):
    """
    Returns anomaly scores (lower = more anomalous)
    """
    scores = model.decision_function(X)
    return scores 