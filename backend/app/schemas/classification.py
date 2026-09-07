from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ClassificationResult(BaseModel):
    """Response shape returned right after POST /classify."""

    id: int
    label: str
    confidence: float
    should_sort: bool
    created_at: datetime

    # Lets Pydantic build this directly from a SQLAlchemy object
    # (model.id, model.label, etc.) instead of needing a dict.
    model_config = ConfigDict(from_attributes=True)


class ClassificationHistoryItem(BaseModel):
    """One row in the GET /history list."""

    id: int
    label: str
    confidence: float
    should_sort: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CategoryBreakdown(BaseModel):
    biodegradable: int = 0
    non_biodegradable: int = 0
    recyclable: int = 0


class StatsResponse(BaseModel):
    """Response shape for GET /stats."""

    total: int
    by_category: CategoryBreakdown
    average_confidence: float