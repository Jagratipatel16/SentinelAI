from pydantic import BaseModel


class PredictionRequest(BaseModel):

    step: int

    type: int

    amount: float

    oldbalanceOrg: float

    newbalanceOrig: float

    oldbalanceDest: float

    newbalanceDest: float

    isFlaggedFraud: int


class PredictionResponse(BaseModel):

    prediction: str

    probability: float

    risk_score: float