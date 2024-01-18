from sqlalchemy import create_engine
from models import Base

# 데이터베이스 설정
SERVER_HOST = "database-1.c3mqckcawht2.ap-southeast-2.rds.amazonaws.com"
USERNAME = "admin"
PASSWORD = "63814110"
DATABASE_NAME = "greedot"

# SQLAlchemy 엔진 생성
engine = create_engine(f"mysql+pymysql://{USERNAME}:{PASSWORD}@{SERVER_HOST}/{DATABASE_NAME}")

# 데이터베이스에 테이블 생성
Base.metadata.create_all(engine)
