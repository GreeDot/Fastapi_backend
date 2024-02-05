from pydantic.v1 import BaseSettings
import secrets
import os

class Settings(BaseSettings):
    API_v1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()

AWS_RDS_ID = 'admin'
AWS_RDS_PASSWORD = '63814110'

# 데이터베이스 설정
DATABASE_URI = f"mysql+pymysql://{AWS_RDS_ID}:{AWS_RDS_PASSWORD}@database-1.c3mqckcawht2.ap-southeast-2.rds.amazonaws.com/greedot"
ASYNC_DATABASE_URI = f"mysql+aiomysql://{AWS_RDS_ID}:{AWS_RDS_PASSWORD}@database-1.c3mqckcawht2.ap-southeast-2.rds.amazonaws.com/greedot"

