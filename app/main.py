# reference: https://github.com/SuiOni/fast-api-sample-project
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from app.api.api import api_router

app = FastAPI()

app.include_router(api_router)