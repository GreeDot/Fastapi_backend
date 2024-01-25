from fastapi import FastAPI, HTTPException, Depends
from .models import Member, RoleEnum, StatusEnum, GradeEnum
from .utils import hash_password
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from config import ASYNC_DATABASE_URI
from sqlalchemy.future import select
from .database import AsyncSessionLocal, get_db, async_engine
app = FastAPI()


# Pydantic 모델 정의 - 사용자 입력을 검증하기 위함
class RegisterRequest(BaseModel):
    email: str
    nickname: str
    password: str

# 비동기 데이터베이스 엔진 생성
engine = async_engine
# 비동기 세션 생성자
AsyncSessionLocal = AsyncSessionLocal

# `user_exists` 함수를 사용하여 이메일 주소로 사용자 존재 여부 확인
async def user_exists(email: str, db_session: AsyncSession) -> bool:
    async with db_session as session:
        # `Member` 모델에서 이메일 주소로 사용자를 조회
        result = await session.execute(select(Member).filter(Member.email == email))
        member = result.scalars().first()
        return member is not None

@app.post('/register')
async def register_member(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # 입력 데이터 검증
    email = request.email
    nickname = request.nickname
    password = request.password

    if await user_exists(request.email, db):
        raise HTTPException(status_code=400, detail="이미 존재하는 사용자입니다.")

    if not email or not nickname or not password:
        raise HTTPException(status_code=400, detail="모든 칸을 입력해주세요")

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
