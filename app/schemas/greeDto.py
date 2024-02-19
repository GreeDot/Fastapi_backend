from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.enums import StatusEnum


class GreeUpdate(BaseModel):
    gree_name: Optional[str] = None
    prompt_gender: Optional[str] = None
    prompt_age: Optional[int] = None
    prompt_mbti: Optional[str] = None
    status: Optional[StatusEnum] = None
    isFavorite: Optional[bool] = None

class Gree(BaseModel):
    id: int
    member_id: int
    gree_name: Optional[str] = Field(default=None)
    raw_img: str
    prompt_gender: Optional[str] = None
    prompt_age: Optional[int] = None
    prompt_mbti: Optional[str] = None
    status: StatusEnum
    isFavorite: bool
    
    class Config:
        from_attributes = True