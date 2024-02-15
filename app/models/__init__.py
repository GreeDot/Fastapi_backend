from sqlalchemy import create_engine

# main.py를 기준으로 하는게 아닌, 프로젝트 루트 경로를 베이스로 한다.
from app.models.models import Base
from app.core.config import DATABASE_URI


def init_db():
    engine = create_engine(DATABASE_URI)
    # Base.metadata.create_all을 호출하여 모든 상속된 테이블을 생성합니다.
    Base.metadata.create_all(engine)
    print("모든 테이블이 생성되었습니다.")


if __name__ == "__main__":
    init_db()