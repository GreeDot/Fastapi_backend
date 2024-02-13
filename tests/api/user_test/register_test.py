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
    # 테스트 데이터베이스 생성 로직을 여기에 통합
    await init_test_db()
    async with AsyncTestingSessionLocal() as db:
        app.dependency_overrides[get_db] = lambda: db
        async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
            yield client

@pytest.mark.asyncio
async def test_register_member_success_async(async_client):
    # 회원가입 정상작동 확인
    register_data = {
        "username": "testuser",
        "nickname": "testnickname",
        "password": "testpassword"
    }

    print('=====회원가입 정상작동 확인=====')
    response = await async_client.post("/api/v1/user/register", json=register_data)
    assert response.status_code == 200
    data = response.json()
    print(f'data = {data}')


    # 회원가입 중복 확인
    register_data = {
        "username": "testuser",
        "nickname": "testnickname",
        "password": "testpassword"
    }

    print('=====회원가입 중복 확인=====')
    response = await async_client.post("/api/v1/user/register", json=register_data)
    assert response.status_code == 400
    data = response.json()
    print(f'data = {response}')

    # 회원가입 빈값 확인(username)
    register_data = {
        "username": "",
        "nickname": "testnickname",
        "password": "testpassword"
    }

    print('=====회원가입 빈값 확인=====')
    response = await async_client.post("/api/v1/user/register", json=register_data)
    assert response.status_code == 400
    data = response.json()
    print(f'data = {response}')

    # 회원가입 빈값 확인(nickname)
    register_data = {
        "username": "testuser",
        "nickname": "",
        "password": "testpassword"
    }

    print('=====회원가입 빈값 확인=====')
    response = await async_client.post("/api/v1/user/register", json=register_data)
    assert response.status_code == 400
    data = response.json()
    print(f'data = {response}')

    # 회원가입 빈값 확인(password)
    register_data = {
        "username": "testuser",
        "nickname": "testnickname",
        "password": ""
    }

    print('=====회원가입 빈값 확인=====')
    response = await async_client.post("/api/v1/user/register", json=register_data)
    assert response.status_code == 400
    data = response.json()
    print(f'data = {response}')
    
    
