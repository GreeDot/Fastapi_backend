from pydantic.v1 import BaseSettings


class Settings(BaseSettings):
    API_v1_STR: str = "/api/v1"
    SECRET_KEY: str = "#나중에 정의#"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()

# 데이터베이스 설정
DATABASE_URI = "mysql+pymysql://admin:63814110@database-1.c3mqckcawht2.ap-southeast-2.rds.amazonaws.com/greedot"
ASYNC_DATABASE_URI = "mysql+aiomysql://admin:63814110@database-1.c3mqckcawht2.ap-southeast-2.rds.amazonaws.com/greedot"
