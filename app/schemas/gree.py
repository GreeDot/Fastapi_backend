from pydantic import BaseModel, Field
from typing import Optional
from models.enums import StatusEnum
from datetime import datetime

class GreeUpdate(BaseModel):
    gree_name: Optional[str] = None
    prompt_character: Optional[str] = None
    prompt_age: Optional[int] = None
    prompt_mbti: Optional[str] = None
    status: Optional[StatusEnum] = None
    isFavorite: Optional[bool] = None


class Gree(BaseModel):
    member_id: int
    gree_name: Optional[str] = Field(default=None)
    raw_img: str
    prompt_character: Optional[str] = None
    prompt_age: Optional[int] = None
    prompt_mbti: Optional[str] = None
    status: StatusEnum
    isFavorite: bool

    class Config:
        orm_mode = True