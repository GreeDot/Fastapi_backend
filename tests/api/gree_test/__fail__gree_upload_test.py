# import httpx
# import pytest
# from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy import text
# from app.models.models import Base
# from app.database import get_db
# from main import app
# import os

# # 환경 변수와 데이터베이스 설정
# aws_rds_id = os.getenv("AWS_RDS_ID")
# aws_rds_password = os.getenv("AWS_RDS_PASSWORD")
# sqlalchemy_test_url = f"mysql+aiomysql://{aws_rds_id}:{aws_rds_password}@database-1.c3mqckcawht2.ap-southeast-2.rds.amazonaws.com/greedottest"

# async_engine = create_async_engine(sqlalchemy_test_url, echo=True)
# AsyncTestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession)

# async def init_test_db():
#     async with async_engine.begin() as conn:
#         await conn.execute(text("DROP DATABASE IF EXISTS greedottest"))
#         await conn.execute(text("CREATE DATABASE greedottest"))
#         await conn.execute(text("USE greedottest"))
#         await conn.run_sync(Base.metadata.create_all)

# @pytest.fixture
# async def async_client():
#     await init_test_db()
#     async with AsyncTestingSessionLocal() as db:
#         app.dependency_overrides[get_db] = lambda: db
#         async with httpx.AsyncClient(app=app, base_url="http://testserver") as client:
#             yield client

# @pytest.mark.asyncio
# async def test_update_gree_raw_img_success(async_client):
#     # 사용자 생성
#     register_data = {
#         "username": "update_profile_user",
#         "nickname": "initial_nickname",
#         "password": "testpassword"
#     }
#     response = await async_client.post("/api/v1/user/register", json=register_data)
#     assert response.status_code == 200

#     # 로그인하여 토큰 받기
#     login_data = {
#         "username": "update_profile_user",
#         "password": "testpassword"
#     }
#     response = await async_client.post("/api/v1/user/login", data=login_data)
#     assert response.status_code == 200
#     token = response.json()['access_token']

#     # 토큰을 사용하여 tests/api/gree_test/testimg/uploadtestimg.png 업로드
#     # 로그인해서 확인
#     current_dir = os.path.dirname(os.path.abspath(__file__))
#     relative_path = r'testimg\uploadtestimg.png'
#     absolute_path = os.path.join(current_dir, relative_path)

#     print(f'absolute_path : {absolute_path}')

#     headers = {"Authorization": f"Bearer {token}"}
#     with open(absolute_path, 'rb') as f:
#         files = {'file': ('uploadtestimg.png', f, 'image/png')}
#         response = await async_client.post("/api/v1/gree/upload-raw-img", files=files, headers=headers)
#     assert response.status_code == 200
#     upload_json_data = response.json()
#     print(upload_json_data)
    
