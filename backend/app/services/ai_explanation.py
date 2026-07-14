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


def generate_explanation(data):

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

    prediction = model.predict(features)[0]

    probability = model.predict_proba(features)[0][1]

    risk_score = round(probability * 100, 2)

    reasons = []

    # Rule 1
    if data.amount > 100000:
        reasons.append("Large transaction amount")

    # Rule 2
    if data.newbalanceOrig == 0:
        reasons.append("Sender account balance became zero")

    # Rule 3
    if data.type == 4:
        reasons.append("TRANSFER transaction detected")

    # Rule 4
    if data.isFlaggedFraud == 1:
        reasons.append("Transaction officially flagged as fraud")

    # Rule 5
    if probability > 0.70:
        reasons.append("Machine Learning model predicts HIGH fraud probability")

    # If no reason found
    if len(reasons) == 0:
        reasons.append("No suspicious activity detected")

    # Prediction Label
    if prediction == 1:
        label = "Fraud"
    else:
        label = "Safe"

    # Recommendation
    if risk_score >= 70:

        recommendation = (
            "Block transaction immediately and perform manual verification."
        )

    elif risk_score >= 30:

        recommendation = (
            "Manual verification is recommended before approval."
        )

    else:

        recommendation = (
            "Transaction appears safe."
        )

    return {

        "prediction": label,

        "risk_score": risk_score,

        "reasons": reasons,

        "recommendation": recommendation

    }