import json
import os

import joblib
import numpy as np
from groq import Groq

from app.core.config import settings

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "fraud_model.pkl"
)

model = joblib.load(MODEL_PATH)

# Groq client is created once and reused across requests
groq_client = Groq(api_key=settings.GROQ_API_KEY) if settings.GROQ_API_KEY else None

TRANSACTION_TYPE_LABELS = {
    0: "CASH_IN",
    1: "CASH_OUT",
    2: "DEBIT",
    3: "PAYMENT",
    4: "TRANSFER",
}


def _rule_based_flags(data, probability):
    """
    Cheap, deterministic signals we can compute locally.
    These are sent to the LLM as context (so it isn't guessing),
    and are also used as a fallback if the LLM call fails.
    """
    flags = []

    if data.amount > 100000:
        flags.append("Large transaction amount")

    if data.newbalanceOrig == 0:
        flags.append("Sender account balance became zero")

    if data.type == 4:
        flags.append("TRANSFER transaction detected")

    if data.isFlaggedFraud == 1:
        flags.append("Transaction officially flagged as fraud")

    if probability > 0.70:
        flags.append("Machine learning model predicts HIGH fraud probability")

    if not flags:
        flags.append("No suspicious activity detected")

    return flags


def _fallback_response(label, risk_score, flags):
    """Used if the LLM call fails or returns something we can't parse."""
    if risk_score >= 70:
        recommendation = "Block transaction immediately and perform manual verification."
    elif risk_score >= 30:
        recommendation = "Manual verification is recommended before approval."
    else:
        recommendation = "Transaction appears safe."

    return {
        "prediction": label,
        "risk_score": risk_score,
        "reasons": flags,
        "recommendation": recommendation,
    }


def _ask_llm(data, label, risk_score, flags):
    """
    Sends the transaction + ML output + rule flags to Groq (Llama model)
    and asks it to return a structured JSON explanation.
    """
    type_label = TRANSACTION_TYPE_LABELS.get(data.type, str(data.type))

    prompt = f"""You are a fraud analyst assistant for a bank. Explain the following
transaction in plain, professional language for a bank employee reading a dashboard.

Transaction details:
- Type: {type_label}
- Amount: {data.amount}
- Sender balance before: {data.oldbalanceOrg}, after: {data.newbalanceOrig}
- Receiver balance before: {data.oldbalanceDest}, after: {data.newbalanceDest}
- Officially flagged as fraud: {bool(data.isFlaggedFraud)}

Machine learning model output:
- Prediction: {label}
- Risk score: {risk_score}/100

Automated rule checks that fired:
{chr(10).join(f"- {f}" for f in flags)}

Respond with ONLY valid JSON (no markdown, no extra text) in this exact shape:
{{
  "reasons": ["short reason 1", "short reason 2", ...],
  "recommendation": "one or two sentence recommended action for the bank employee"
}}
Keep each reason under 15 words. Base the reasons on the data given above, don't invent numbers."""

    response = groq_client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=400,
    )

    content = response.choices[0].message.content.strip()

    # Models sometimes wrap JSON in ```json ... ``` even when told not to
    if content.startswith("```"):
        content = content.strip("`")
        content = content.replace("json", "", 1).strip()

    parsed = json.loads(content)

    return {
        "prediction": label,
        "risk_score": risk_score,
        "reasons": parsed["reasons"],
        "recommendation": parsed["recommendation"],
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

    # We derive the label directly from the probability instead of calling
    # model.predict() separately. Some XGBoost pickle/version combinations can
    # make predict() and predict_proba() disagree slightly - using a single
    # source of truth (the probability) guarantees the label and risk_score
    # are always consistent with each other.
    probability = model.predict_proba(features)[0][1]
    risk_score = round(float(probability) * 100, 2)
    label = "Fraud" if probability >= 0.5 else "Safe"

    flags = _rule_based_flags(data, probability)

    # If no API key configured, or the LLM call fails for any reason,
    # fall back to the rule-based explanation so the endpoint never breaks.
    if groq_client is None:
        return _fallback_response(label, risk_score, flags)

    try:
        return _ask_llm(data, label, risk_score, flags)
    except Exception as e:
        print(f"[ai_explanation] LLM call failed, using fallback: {e}")
        return _fallback_response(label, risk_score, flags)