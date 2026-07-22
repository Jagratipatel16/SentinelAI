import joblib
import numpy as np
import os


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "fraud_model.pkl"
)

model = joblib.load(MODEL_PATH)

def predict_transaction(data):

    features = np.array([[
        data.step,
        data.type,
        data.amount,
        data.oldbalanceOrg,
        data.newbalanceOrig,
        data.oldbalanceDest,
        data.newbalanceDest,
        data.isFlaggedFraud
    ]])

    # Derive the label directly from the probability (single source of truth)
    # instead of calling model.predict() separately, so the label and
    # risk_score can never disagree with each other.
    probability = model.predict_proba(features)[0][1]

    risk_score = round(probability * 100, 2)

    if probability >= 0.5:
        label = "Fraud"
    else:
        label = "Safe"

    return {

        "prediction": label,

        "probability": round(float(probability),4),

        "risk_score": risk_score

    }