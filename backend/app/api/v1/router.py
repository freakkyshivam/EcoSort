from fastapi import APIRouter

from app.api.v1 import classify, stats

router = APIRouter()
router.include_router(classify.router, tags=["classify"])
router.include_router(stats.router, tags=["stats"])