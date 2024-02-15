from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.enums import LogTypeEnum

# 생성을 위한 DTO
class CreateUserTalkLogDto(BaseModel):
    gree_id: int
    log_type: LogTypeEnum
    content: str

class CreateGreeTalkLogDto(BaseModel):
    gree_id: int
    log_type: LogTypeEnum
    content: str
    voice_url: str # azure

# 응답을 위한 DTO
class LogResponseDto(BaseModel):
    id: int
    gree_id: int
    log_type: LogTypeEnum
    content: Optional[str] = None
    register_at: datetime

    class Config:
        from_attributes = True
