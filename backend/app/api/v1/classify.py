from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.classification import Classification
from app.schemas.classification import ClassificationResult
from app.services.inference import InferenceService, get_inference_service

router = APIRouter()

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.post("/classify", response_model=ClassificationResult)
async def classify_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    inference: InferenceService = Depends(get_inference_service),
):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{file.content_type}'. Use JPEG, PNG, or WEBP.",
        )

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    result = inference.classify_image(image_bytes)

    record = Classification(
        label=result["label"],
        confidence=result["confidence"],
        should_sort=result["should_sort"],
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return record