from fastapi import FastAPI, HTTPException
from .models import Member, RoleEnum, StatusEnum, GradeEnum
from .utils import hash_password
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config import ASYNC_DATABASE_URI

# Pydantic 모델 정의 - 사용자 입력을 검증하기 위함
class RegisterRequest(BaseModel):
    email: str
    nickname: str
    password: str

app = FastAPI()
# 비동기 데이터베이스 엔진 생성
engine = create_async_engine(ASYNC_DATABASE_URI)
# 비동기 세션 생성자
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

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
        register_at= datetime.now()# 현재 시간 설정
    )
    async with AsyncSessionLocal() as session:
        async with session.begin():
            try:
                session.add(new_member)
                # 비동기 커밋
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise HTTPException(status_code=500, detail=f"회원가입 실패: {e}")

    return {"message": "회원가입이 완료되었습니다."}
