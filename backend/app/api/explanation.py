from fastapi import APIRouter

from app.schemas.explanation import (
    ExplanationRequest,
    ExplanationResponse
)

from app.services.ai_explanation import generate_explanation


router = APIRouter(

    prefix="/explanation",

    tags=["AI Explanation"]

)


@router.post(
    "/",
    response_model=ExplanationResponse
)
def explain_transaction(data: ExplanationRequest):

    return generate_explanation(data)