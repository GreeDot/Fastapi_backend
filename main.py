# main.py
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings

# Alembic 관련 임포트
from alembic.config import Config
from alembic import command

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

def run_alembic_upgrade():
    """Alembic을 사용하여 자동으로 리비전을 생성하고 
    데이터베이스를 최신 상태로 마이그레이션합니다."""
    alembic_cfg = Config("alembic.ini")
    command.revision(alembic_cfg, message="Add table", autogenerate=True)
    command.stamp(alembic_cfg, "head")
    command.upgrade(alembic_cfg, "head")

if __name__ == "__main__":
    run_alembic_upgrade()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="debug")
