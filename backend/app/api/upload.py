from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from app.schemas.upload import UploadResponse

from app.services.upload_service import process_csv
from app.database.session import get_db
from fastapi.responses import FileResponse
import os

router = APIRouter(

    prefix="/upload",

    tags=["CSV Upload"]

)


@router.post("/", response_model=UploadResponse)
def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    if not file.filename.endswith(".csv"):

        raise HTTPException(
            status_code=400,
            detail="Please upload a CSV file."
        )

    try:

        result = process_csv(file, db)

    except ValueError as e:

        raise HTTPException(status_code=400, detail=str(e))

    except KeyError as e:

        raise HTTPException(
            status_code=400,
            detail=f"CSV is missing a required column: {e}"
        )

    except Exception as e:

        print("UPLOAD ERROR:", str(e))

        raise HTTPException(status_code=500, detail=str(e))

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