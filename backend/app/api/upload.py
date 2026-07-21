from fastapi import APIRouter, UploadFile, File, HTTPException

from app.schemas.upload import UploadResponse

from app.services.upload_service import process_csv
from fastapi.responses import FileResponse
import os

router = APIRouter(

    prefix="/upload",

    tags=["CSV Upload"]

)


@router.post("/", response_model=UploadResponse)
def upload_csv(file: UploadFile = File(...)):

    try:

        if not file.filename.endswith(".csv"):

            raise HTTPException(
                status_code=400,
                detail="Please upload a CSV file."
            )

        result = process_csv(file)

        return result

    except Exception as e:

        print("UPLOAD ERROR:", str(e))

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    return FileResponse(

        path=file_path,

        filename=filename,

        media_type="text/csv"

    )