# tests/user_test/login_test.py
import httpx
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.models.models import Base
from app.database import get_db
from main import app
import os

aws_rds_id = os.getenv("AWS_RDS_ID")
aws_rds_password = os.getenv("AWS_RDS_PASSWORD")
sqlalchemy_test_url = f"mysql+aiomysql://{aws_rds_id}:{aws_rds_password}@database-1.c3mqckcawht2.ap-southeast-2.rds.amazonaws.com/greedottest"

async_engine = create_async_engine(sqlalchemy_test_url, echo=True)
AsyncTestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession)

async def init_test_db():
    async with async_engine.begin() as conn:
        await conn.execute(text("DROP DATABASE IF EXISTS greedottest"))
        await conn.execute(text("CREATE DATABASE greedottest"))
        await conn.execute(text("USE greedottest"))
        await conn.run_sync(Base.metadata.create_all)

@pytest.fixture
async def async_client():
    await init_test_db()
    async with AsyncTestingSessionLocal() as db:
        app.dependency_overrides[get_db] = lambda: db
        async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
            yield client

@pytest.mark.asyncio
async def test_login_member_success_async(async_client):
    # 목업 데이터 준비
    print('=====목업 데이터 준비=====')
    MODIFIED_PASSWORD = "modified_password"
    MODIFIED_NICKNAME = "modified_nickname"
    TESTUSER = "testuser"

    register_data = {
        "username": TESTUSER,
        "nickname": "testnickname",
        "password": "testpassword"
    }
    
    response = await async_client.post("/api/v1/user/register", json=register_data)
    assert response.status_code == 200

    
    print('=====user_put 정상작동 확인(회원 정보 수정 후 로그인 시도)=====')
    put_data = {
        "nickname": MODIFIED_NICKNAME,
        "password": MODIFIED_PASSWORD
    }
    response = await async_client.put("/api/v1/user/1", json=put_data)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    data = response.json()
    print(f'data = {data}')
    assert data["nickname"] == MODIFIED_NICKNAME

    # 변경된 비밀번호로 로그인 시도
    login_data = {
        "username": TESTUSER,
        "password": MODIFIED_PASSWORD
    }
    try:
        response = await async_client.post("/api/v1/user/login", data=login_data)
    except:
        print(Exception)

    # 로그인 성공 확인
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    data = response.json()
    assert data['access_token'] is not None, "Access token should not be None for successful login"
