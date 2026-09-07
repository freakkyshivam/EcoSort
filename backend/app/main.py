from fastapi import FastAPI

from app.api.v1.router import router as api_v1_router
from app.config import settings
from app.database import Base, engine

# Creates the classifications table if it doesn't already exist.
# Fine for a hackathon project; a real production app would use
# proper migrations (Alembic) instead of this.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="EcoSort API", version="0.1.0")

app.include_router(api_v1_router, prefix=settings.api_v1_prefix)


@app.get("/health")
def health_check():
    return {"status": "ok"}