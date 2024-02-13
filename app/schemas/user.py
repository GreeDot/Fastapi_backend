from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.enums import RoleEnum, StatusEnum, GradeEnum


# 사용자 생성 스키마
class UserCreate(BaseModel):
    username: str
    nickname: str
    password: str


# 사용자 업데이트 스키마
class UserUpdate(BaseModel):
    nickname: Optional[str] = None
    password: Optional[str] = None


# 사용자 조회 스키마
class User(BaseModel):
    id: int
    username: str
    nickname: str
    role: RoleEnum
    status: StatusEnum
    grade: GradeEnum
    refresh_token: Optional[str] = None
    register_at: datetime

    class Config:
        from_attributes = True
        use_enum_values = True
