from sqlalchemy import create_engine
from .base import Base
from .models import Member, Gree, Log, GreeFile, EmotionReport
from core.config import DATABASE_URI


def init_db():
    engine = create_engine(DATABASE_URI)
    # Base.metadata.create_all을 호출하여 모든 상속된 테이블을 생성합니다.
    Base.metadata.create_all(engine)
    print("모든 테이블이 생성되었습니다.")


if __name__ == "__main__":
    init_db()