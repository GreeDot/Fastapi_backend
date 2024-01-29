import uvicorn
from fastapi import FastAPI
from api.router import api_router
from core.config import settings
app = FastAPI()


# API 라우터를 앱에 포함
app.include_router(api_router, prefix=settings.API_v1_STR)


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)