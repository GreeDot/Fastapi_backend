from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import ASYNC_DATABASE_URI

# 비동기 엔진 생성
async_engine = create_async_engine(ASYNC_DATABASE_URI)

# 비동기 세션 생성자
AsyncSessionLocal = sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False)


# 비동기 데이터베이스 세션 제공자 정의
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
