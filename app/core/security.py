from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
import jwt
from fastapi.security import OAuth2PasswordBearer
import bcrypt
from fastapi import HTTPException, status
from pydantic import BaseModel
from .config import settings

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = None  # 토큰의 만료 시간 (옵션)
    user_role: str = None  # 사용자의 역할 (옵션)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/login")

def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')

    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    # Enum 값을 문자열로 변환
    if "role" in to_encode and isinstance(to_encode["role"], Enum):
        to_encode["role"] = to_encode["role"].value

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)  # 예시: 15분 후 만료
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    expires_in = expires_delta.total_seconds() if expires_delta else 15 * 60  # 예시 값

    # Token 생성 시 user_role에도 Enum의 value를 사용
    return Token(
        access_token=encoded_jwt,
        token_type="bearer",
        expires_in=expires_in,
        user_role=to_encode.get("role")  # 이미 문자열로 변환된 값 사용
    )


# 토큰을 검증하고 페이로드 반환, 유효하지 않은 경우 예외 발생
def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM], options={"verify_exp": True})
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
