import json
import joblib
import numpy as np
import os

from groq import Groq
from app.core.config import settings

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "fraud_model.pkl"
)

model = joblib.load(MODEL_PATH)

client = None

if settings.GROQ_API_KEY:
    client = Groq(api_key=settings.GROQ_API_KEY)


def rule_based_result(label, risk_score, reasons):

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

    if data.amount > 100000:
        reasons.append("Large transaction amount")

    if data.newbalanceOrig == 0:
        reasons.append("Sender account balance became zero")

    if data.type == 4:
        reasons.append("TRANSFER transaction detected")

    if data.isFlaggedFraud == 1:
        reasons.append("Transaction officially flagged as fraud")

    if probability > 0.70:
        reasons.append("Machine Learning model predicts HIGH fraud probability")

    if len(reasons) == 0:
        reasons.append("No suspicious activity detected")

    label = "Fraud" if prediction == 1 else "Safe"

    fallback = rule_based_result(
        label,
        risk_score,
        reasons
    )

    if client is None:
        return fallback

    TYPE_MAP = {
        1: "PAYMENT",
        2: "CASH_OUT",
        3: "DEBIT",
        4: "TRANSFER",
        5: "CASH_IN"
    }

    transaction_type = TYPE_MAP.get(data.type, "UNKNOWN")

    prompt = f"""
You are an expert financial fraud analyst.

Analyze the following bank transaction.

Transaction Details

Transaction Type: {transaction_type}

Amount: {data.amount}

Old Sender Balance: {data.oldbalanceOrg}

New Sender Balance: {data.newbalanceOrig}

Old Receiver Balance: {data.oldbalanceDest}

New Receiver Balance: {data.newbalanceDest}

ML Prediction: {label}

Risk Score: {risk_score}

Detected Indicators:
{", ".join(reasons)}

Return ONLY valid JSON in this format:

{{
    "prediction":"Fraud or Safe",
    "risk_score": {risk_score},
    "reasons":[
        "Reason 1",
        "Reason 2",
        "Reason 3"
    ],
    "recommendation":"Detailed recommendation"
}}

Do not use markdown.
Do not use triple backticks.
Do not write any extra explanation.
"""

    try:

        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            temperature=0.2,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        answer = response.choices[0].message.content.strip()

        print("\n========== LLM RESPONSE ==========")
        print(answer)
        print("==================================\n")

        if answer.startswith("```"):
            answer = answer.replace("```json", "")
            answer = answer.replace("```", "")
            answer = answer.strip()

        result = json.loads(answer)

        return result

    except Exception as e:

        import traceback

        traceback.print_exc()

        print("Groq Error:", repr(e))

        return fallback