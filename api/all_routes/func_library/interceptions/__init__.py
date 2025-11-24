from fastapi import APIRouter

from .x_interception_rute import router as x_router
from .y_interception_rute import router as y_router

router = APIRouter()
router.include_router(x_router)
router.include_router(y_router)

__all__ = ["router"]

