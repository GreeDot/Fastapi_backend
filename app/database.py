from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models import Base
from config import ASYNC_DATABASE_URI, DATABASE_URI

# SQLAlchemy 엔진 생성
engine = create_engine(DATABASE_URI)

# 비동기 엔진 생성
async_engine = create_async_engine(ASYNC_DATABASE_URI)

# 비동기 세션 생성자
AsyncSessionLocal = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)

# 데이터베이스에 테이블 생성
Base.metadata.create_all(engine)

#비동기 데이터베이스 세션 제공자 정의
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session