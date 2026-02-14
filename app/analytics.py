from app.database import get_connection
from sklearn.linear_model import LogisticRegression
import numpy as np

def encode_urgency(urgency):
    return {"low": 0, "medium": 1, "high": 2}.get(urgency, 1)

def encode_sentiment(sentiment):
    return {"positive": 0, "neutral": 1, "negative": 2}.get(sentiment, 1)

def encode_behavior(behavior):
    return {"polite": 0, "neutral": 1, "rude": 2, "unknown": 3}.get(behavior, 1)

def encode_category_risk(category, all_rows):
    # Calculate historical resolution rate for this category
    category_calls = [r for r in all_rows if category in (r[3] or "")]
    if len(category_calls) < 3:
        return 0.5  # Default risk
    
    unresolved = sum(1 for r in category_calls if r[4] == "unresolved")
    return unresolved / len(category_calls)  # Risk score 0-1

def calculate_operational_risk():
    # 1. Fetch all calls
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT urgency, sentiment, agent_behavior, issue_category, call_outcome
            FROM support_calls
        """)
        rows = cursor.fetchall()
    
    if len(rows) < 10:
        return {
            "risk_score": 0,
            "level": "Insufficient Data",
            "message": "Need at least 10 calls for prediction"
        }
    
    # 2. Prepare features
    X = []
    y = []
    
    for row in rows:
        # Target: 1 if unresolved, 0 if resolved
        y.append(1 if row[4] == "unresolved" else 0)
        
        # Features
        features = [
            encode_urgency(row[0]),
            encode_sentiment(row[1]),
            encode_behavior(row[2]),
            encode_category_risk(row[3], rows)
        ]
        X.append(features)
    
    # 3. Train model
    model = LogisticRegression(max_iter=1000)
    model.fit(X, y)
    
    # 4. Get average predicted risk
    predictions = model.predict_proba(X)[:, 1]
    avg_risk = np.mean(predictions) * 100
    
    # 5. Get top contributing factor
    feature_names = ["urgency", "sentiment", "behavior", "category"]
    coefficients = model.coef_[0]
    top_idx = np.argmax(np.abs(coefficients))
    top_factor = feature_names[top_idx]
    top_direction = "increases" if coefficients[top_idx] > 0 else "decreases"
    
    # 6. Determine level
    if avg_risk < 30:
        level = "Low"
    elif avg_risk < 60:
        level = "Medium"
    else:
        level = "High"
    
    return {
        "risk_score": round(avg_risk, 1),
        "level": level,
        "top_factor": {
            "name": top_factor,
            "impact": top_direction,
            "coefficient": round(coefficients[top_idx], 3)
        },
        "total_calls_used": len(rows)
    }