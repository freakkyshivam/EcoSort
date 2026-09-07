from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.classification import Classification
from app.schemas.classification import (
    CategoryBreakdown,
    ClassificationHistoryItem,
    StatsResponse,
)

router = APIRouter()


@router.get("/history", response_model=list[ClassificationHistoryItem])
def get_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    records = (
        db.query(Classification)
        .order_by(Classification.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return records


@router.get("/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(Classification.id)).scalar() or 0

    counts_by_label = dict(
        db.query(Classification.label, func.count(Classification.id))
        .group_by(Classification.label)
        .all()
    )

    avg_confidence = db.query(func.avg(Classification.confidence)).scalar() or 0.0

    return StatsResponse(
        total=total,
        by_category=CategoryBreakdown(
            biodegradable=counts_by_label.get("biodegradable", 0),
            non_biodegradable=counts_by_label.get("non_biodegradable", 0),
            recyclable=counts_by_label.get("recyclable", 0),
        ),
        average_confidence=round(avg_confidence, 4),
    )