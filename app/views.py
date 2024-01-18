from fastapi import FastAPI, HTTPException, Body
from .models import Member, RoleEnum, StatusEnum, GradeEnum
from .utils import hash_password
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from config import DATABASE_URI
from pydantic import BaseModel
from datetime import datetime

# Pydantic 모델 정의 - 사용자 입력을 검증하기 위함
class RegisterRequest(BaseModel):
    email: str
    nickname: str
    password: str


app = FastAPI()

# 데이터베이스 연결 설정
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)


@app.post('/register')
async def register_member(request: RegisterRequest):
    # 입력 데이터 검증
    email = request.email
    nickname = request.nickname
    password = request.password

    if not email or not nickname or not password:
        raise HTTPException(status_code=400, detail="모든 필드를 입력해야 합니다.")

    # 비밀번호 해싱
    hashed_pwd = hash_password(password)

    # 새 회원 객체 생성
    new_member = Member(
        email=email,
        nickname=nickname,
        password=hashed_pwd,
        role=RoleEnum.MEMBER,  # 기본 역할 설정
        status=StatusEnum.ACTIVATE,  # 기본 상태 설정
        grade=GradeEnum.FREE,  # 기본 등급 설정
        register_at=datetime.now()  # 현재 시간 설정
    )

    # 데이터베이스에 삽입
    session = Session()
    try:
        session.add(new_member)
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"회원가입 실패: {e}")
    finally:
        session.close()

    return {"message": "회원가입이 완료되었습니다."}
