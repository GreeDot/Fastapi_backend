import uvicorn
from fastapi import FastAPI
from api.router import api_router
from core.config import settings
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인에서의 접근을 허용
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메소드 허용
    allow_headers=["*"],  # 모든 HTTP 헤더 허용
)

# API 라우터를 앱에 포함
app.include_router(api_router, prefix=settings.API_v1_STR)



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="debug")
