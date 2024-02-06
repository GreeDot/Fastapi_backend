from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime
from sqlalchemy.future import select
from typing import List, Optional
from starlette.responses import JSONResponse
from models.models import Member, RoleEnum, StatusEnum, GradeEnum
from core.security import hash_password, verify_password, create_access_token
from database import get_db
from pydantic import BaseModel
from crud.crud_user import get_users as crud_get_users, \
    update_user as crud_update_user, \
    delete_user as crud_delete_user
from schemas.user import User, UserUpdate

router = APIRouter()

# Pydantic 모델 정의
class RegisterRequest(BaseModel):
    email: str
    nickname: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# 이메일 중복 확인
async def user_exists(email: str, db_session: AsyncSession) -> bool:
    async with db_session as session:
        result = await session.execute(select(Member).where(Member.email == email))
        member = result.scalars().first()
        return member is not None

## 이메일이 일치한지 확인
async def authenticate_user(email: str, password: str, db: AsyncSession) -> Optional[Member]:
    async with db as session:
        result = await session.execute(select(Member).where(Member.email == email))
        user = result.scalars().first()
        if user and verify_password(password, user.password):
            return user
    return None

# 회원가입 엔드포인트
@router.post('/register')
async def register_member(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    if await user_exists(request.email, db):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 존재하는 사용자입니다.")
    hashed_pwd = hash_password(request.password)
    new_member = Member(
        email=request.email,
        nickname=request.nickname,
        password=hashed_pwd,
        role=RoleEnum.MEMBER,
        status=StatusEnum.ACTIVATE,
        grade=GradeEnum.FREE,
        register_at=datetime.now()
    )
    db.add(new_member)
    await db.commit()
    await db.refresh(new_member)
    return {"message": "회원가입이 성공적으로 완료되었습니다.", "user_id": new_member.id}

# 로그인 엔드포인트
@router.post('/login', response_model=Token)
async def login_for_access_token(db: AsyncSession = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

# 사용자 전체 조회 엔드포인트
@router.get("/users/", response_model=List[User])
async def read_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    users = await crud_get_users(db, skip=skip, limit=limit)
    return users

# 사용자 정보 업데이트 엔드포인트
@router.put("/users/{user_id}", response_model=User)
async def update_user_endpoint(user_id: int, user: UserUpdate, db: AsyncSession = Depends(get_db)):
    updated_user = await crud_update_user(db, user_id, user)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

# 사용자 삭제 엔드포인트
@router.delete("/users/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user_endpoint(user_id: int, db: AsyncSession = Depends(get_db)):
    deletion_successful = await crud_delete_user(db, user_id)
    if deletion_successful:
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "User successfully deleted"})
    else:
        raise HTTPException(status_code=404, detail="User not found")

# 테스트 라우터
@router.get('/test')
async def test():
    return "hello test!!!! 4트"