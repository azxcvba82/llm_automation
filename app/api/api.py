from fastapi import APIRouter
from app.api.endpoints import llm

api_router = APIRouter()

api_router.include_router(llm.router)