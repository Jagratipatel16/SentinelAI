from pydantic import BaseModel


class ExplanationRequest(BaseModel):

    step: int

    type: int

    amount: float

    oldbalanceOrg: float

    newbalanceOrig: float

    oldbalanceDest: float

    newbalanceDest: float

    isFlaggedFraud: int


class ExplanationResponse(BaseModel):

    prediction: str

    risk_score: float

    reasons: list[str]

    recommendation: str