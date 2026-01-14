# ai/fraud.py
import os
import joblib
import numpy as np

MODEL_PATH = "ai/artifacts/fraud_model.pkl"
VECT_PATH  = "ai/artifacts/fraud_vectorizer.pkl"

def predict_fraud(title: str, description: str, threshold: float = 0.55):
    """
    Returns (is_fraud: bool, fraud_confidence: float)
    fraud_confidence is P(label==1)
    """
    if not os.path.exists(MODEL_PATH) or not os.path.exists(VECT_PATH):
        raise FileNotFoundError("Fraud model not trained. Run: python -m ai.train_fraud")

    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECT_PATH)

    text = f"{title} {description}"
    X = vectorizer.transform([text])

    # Default: assume not fraud
    fraud_conf = 0.0

    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)[0]

        # Find the index for class 1 safely
        if hasattr(model, "classes_"):
            classes = list(model.classes_)
            if 1 in classes:
                idx = classes.index(1)
                fraud_conf = float(proba[idx])
            else:
                # If 1 not in classes, fallback to predicted label
                pred = int(model.predict(X)[0])
                fraud_conf = 1.0 if pred == 1 else 0.0
        else:
            pred = int(model.predict(X)[0])
            fraud_conf = 1.0 if pred == 1 else 0.0
    else:
        pred = int(model.predict(X)[0])
        fraud_conf = 1.0 if pred == 1 else 0.0

    is_fraud = fraud_conf >= threshold
    return is_fraud, fraud_conf
