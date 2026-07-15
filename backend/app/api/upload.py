from fastapi import APIRouter, UploadFile, File, HTTPException

from app.schemas.upload import UploadResponse

from app.services.upload_service import process_csv
from fastapi.responses import FileResponse
import os

router = APIRouter(

    prefix="/upload",

    tags=["CSV Upload"]

)


@router.post(

    "/",

    response_model=UploadResponse

)

def upload_csv(

    file: UploadFile = File(...)

):

    # Check CSV File

    if not file.filename.endswith(".csv"):

        raise HTTPException(

            status_code=400,

            detail="Please upload a CSV file."

        )

    # Process CSV

    result = process_csv(file)

    return result

@router.get("/download/{filename}")

def download_file(filename: str):

    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

    file_path = os.path.join(

        BASE_DIR,

        "uploads",

        filename

    )

    if not os.path.exists(file_path):

        raise HTTPException(

            status_code=404,

            detail="File not found."

        )

    return FileResponse(

        path=file_path,

        filename=filename,

        media_type="text/csv"

    )