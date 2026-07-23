from fastapi import APIRouter, UploadFile, File, HTTPException

from app.schemas.explanation import (
    ExplanationRequest,
    ExplanationResponse,
    BatchExplanationResponse
)

from app.services.ai_explanation import generate_explanation, generate_batch_explanation


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


@router.post(
    "/batch-csv",
    response_model=BatchExplanationResponse
)
def explain_csv(file: UploadFile = File(...)):

    if not file.filename.endswith(".csv"):

        raise HTTPException(
            status_code=400,
            detail="Please upload a CSV file."
        )

    try:

        return generate_batch_explanation(file)

    except ValueError as e:

        raise HTTPException(status_code=400, detail=str(e))

    except KeyError as e:

        raise HTTPException(
            status_code=400,
            detail=f"CSV is missing a required column: {e}"
        )