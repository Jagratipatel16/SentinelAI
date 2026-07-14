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
print(MODEL_PATH)

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

    prediction = model.predict(features)[0]

    probability = model.predict_proba(features)[0][1]

    risk_score = round(probability * 100, 2)

    if prediction == 1:
        label = "Fraud"
    else:
        label = "Safe"

    return {

        "prediction": label,

        "probability": round(float(probability),4),

        "risk_score": risk_score

    }