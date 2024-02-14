from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.enums import LogTypeEnum

# 생성을 위한 DTO
class CreateLogDto(BaseModel):
    gree_id: int
    log_type: LogTypeEnum
    content: str

# 응답을 위한 DTO
class LogResponseDto(BaseModel):
    id: int
    gree_id: int
    log_type: LogTypeEnum
    content: Optional[str] = None
    register_at: datetime

    class Config:
        from_attributes = True
