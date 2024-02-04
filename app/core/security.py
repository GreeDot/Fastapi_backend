from datetime import datetime, timedelta
import jwt
from fastapi.security import OAuth2PasswordBearer
import bcrypt
from fastapi import HTTPException, status
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')

    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

# 토큰을 검증하고 페이로드 반환, 유효하지 않은 경우 예외 발생
def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM], options={"verify_exp": True})
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
