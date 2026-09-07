from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

# connect_args is only needed for SQLite (allows use across FastAPI's
# multiple request threads). It's ignored/unnecessary for Postgres/Neon,
# so when you switch database_url later, drop this if-check or leave it —
# it's harmless either way.
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """All SQLAlchemy models (tables) inherit from this."""
    pass


def get_db():
    """
    FastAPI dependency — gives each request its own DB session,
    and guarantees it's closed afterward even if an error occurs.

    Used in route functions like:
        def some_route(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()