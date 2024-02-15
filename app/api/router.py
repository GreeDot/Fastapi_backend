from fastapi import APIRouter
from app.api.api_v1.endpoints import user, gree, log, ai

api_router = APIRouter()
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(gree.router, prefix="/gree", tags=["gree"])
api_router.include_router(log.router, prefix="/log", tags=["log"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])