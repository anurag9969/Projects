import sqlite3
import pandas as pd

DB_PATH = "feedback/feedback.db"

def load_feedback():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM feedback", conn)
    conn.close()
    return df


def monitor_model():
    df = load_feedback()

    if df.empty:
        print("No feedback available yet.")
        return

    total = len(df)
    false_positives = ((df["model_decision"] == 2) & (df["human_label"] == 0)).sum()
    missed_fraud = ((df["model_decision"] != 2) & (df["human_label"] == 1)).sum()

    print("\n--- Monitoring Report ---")
    print(f"Total feedback samples: {total}")
    print(f"False positives (blocked but legit): {false_positives}")
    print(f"Missed fraud (not blocked but fraud): {missed_fraud}")

    # Simple retraining rules
    if false_positives / total > 0.3:
        print("⚠️ Alert: High false positive rate → consider threshold tuning")

    if missed_fraud > 0:
        print("⚠️ Alert: Missed fraud detected → consider retraining")

    if total >= 100:
        print("📌 Sufficient new labels collected → retraining recommended")
