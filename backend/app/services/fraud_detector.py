def detect_fraud(amount: float):

    if amount >= 100000:
        return "Fraud"

    elif amount >= 50000:
        return "Suspicious"

    return "Safe"