import jwt
from jose.exceptions import JWTError
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime
from datetime import timedelta
from sqlalchemy.future import select
from typing import List, Optional
from starlette.responses import JSONResponse
from core.config import settings
from models.models import Member, RoleEnum, StatusEnum, GradeEnum
from core.security import hash_password, verify_password, create_access_token, oauth2_scheme, Token
from database import get_db
from pydantic import BaseModel
from crud.crud_user import get_users as crud_get_users, \
    update_user as crud_update_user, \
    delete_user as crud_delete_user, \
    get_user as crud_get_user
from schemas.user import User, UserUpdate

router = APIRouter()


# Pydantic 모델 정의
class RegisterRequest(BaseModel):
    username: str
    nickname: str
    password: str


# 이메일 중복 확인
async def user_exists(username: str, db_session: AsyncSession) -> bool:
    async with db_session as session:
        result = await session.execute(select(Member).where(Member.username == username))
        member = result.scalars().first()
        return member is not None

## 이메일이 일치한지 확인
async def authenticate_user(username: str, password: str, db: AsyncSession) -> Optional[Member]:
    async with db as session:
        result = await session.execute(select(Member).where(Member.username == username))
        user = result.scalars().first()
        if user and verify_password(password, user.password):
            return user
    return None


async def get_current_user(db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)) -> Member:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    async with db as session:
        result = await session.execute(select(Member).filter(Member.username == username))
        user = result.scalars().first()
        if user is None:
            raise credentials_exception
        return user


# 회원가입 엔드포인트
@router.post('/register')
async def register_member(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    if await user_exists(request.username, db):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미 존재하는 사용자입니다.")
    hashed_pwd = hash_password(request.password)
    new_member = Member(
        username=request.username,
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
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},  # 사용자 역할 정보 추가
        expires_delta=access_token_expires
    )
    return access_token

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


@router.get('/user/profile', response_model=User)
async def read_user_profile(current_user: Member = Depends(get_current_user), db: AsyncSession = Depends(get_db)) -> Optional[User]:
    # 현재 로그인한 사용자의 정보 조회
    user = await crud_get_user(db, current_user.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put('/user/change-profile', response_model=User)
async def update_user_profile(update_request: UserUpdate, current_user: Member = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # 이메일은 수정되지 않도록, UserUpdate 모델에서 이메일 필드를 제외하거나 무시합니다.
    updated_user = await crud_update_user(db, current_user.id, update_request)
    return updated_user


# @router.post('/user/refresh', response_model=Token)
# async def refresh_access_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
#     # 리프레시 토큰 검증 로직 구현
#     # 새 액세스 토큰 생성 및 반환
#     return {"access_token": new_access_token, "token_type": "bearer"}


# @router.post('/user/logout')
# async def logout_user(db: AsyncSession = Depends(get_db), current_user: Member = Depends(get_current_user)):
#     # 필요한 경우 로그아웃 처리 로직 구현
#     # 예: 리프레시 토큰 무효화
#     return {"message": "Successfully logged out"}



# 테스트 라우터
@router.get('/test')
async def test():
    return "hello test!!!! 4트"