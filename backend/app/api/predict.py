from fastapi import APIRouter

from app.schemas.prediction import (
    PredictionRequest,
    PredictionResponse
)

from app.services.predictor import predict_transaction


router = APIRouter(

    prefix="/predict",

    tags=["Prediction"]

)


@router.post(
    "/",
    response_model=PredictionResponse
)
def predict(data: PredictionRequest):

    return predict_transaction(data)