from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Classification(Base):
    """
    One row = one image the ML model classified.

    image_path is nullable on purpose — you told me you're not sure yet
    whether to store images. Leaving it NULL for now costs nothing, and
    you can start populating it later without any migration, since the
    column already exists.
    """

    __tablename__ = "classifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # "biodegradable" | "non_biodegradable" | "recyclable"
    label: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    confidence: Mapped[float] = mapped_column(Float, nullable=False)

    # True if confidence >= threshold at the time of classification
    should_sort: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # Reserved for later — path/URL to a saved image, if you decide to store them
    image_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )