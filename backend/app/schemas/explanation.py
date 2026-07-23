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


class BatchExplanationItem(BaseModel):
    row: int
    sender: str
    receiver: str
    amount: float
    type: str
    risk_score: float
    reasons: list[str]
    recommendation: str


class BatchExplanationResponse(BaseModel):
    total_records: int
    fraud_count: int
    explanations: list[BatchExplanationItem]