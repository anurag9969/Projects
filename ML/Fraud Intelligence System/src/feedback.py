import sqlite3
from datetime import datetime

DB_PATH = "feedback/feedback.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback(
          id INTEGER PRIMARY KEY AUTOINCREMENT, 
          transaction_index INTEGER, 
          model_risk_score REAL, 
          model_decision INTEGER, 
          human_label INTEGER, 
          timestamp TEXT         
                   )
""")
    
    conn.commit()
    conn.close()

def store_feedback(
        transaction_index, 
        model_risk_score, 
        model_decision, 
        human_label
):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO feedback (
                   transaction_index,
                   model_risk_score,
                   model_decision,
                   human_label,
                   timestamp
    ) VALUES (?, ?, ?, ?, ?)
    """, (
        transaction_index,
        model_risk_score,
        model_decision,
        human_label,
        datetime.utcnow().isoformat()

    ))

    conn.commit()
    conn.close()
    