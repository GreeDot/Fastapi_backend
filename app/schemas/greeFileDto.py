from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.enums import FileTypeEnum

class GreeFileSchema(BaseModel):
    id: int
    gree_id: int
    file_type: FileTypeEnum
    file_name: str
    real_name: str
    register_at: datetime