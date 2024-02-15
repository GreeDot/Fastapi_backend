from pydantic import BaseModel

class ChatRequestTestDto(BaseModel):
    name: str
    age: str
    gender: str
    mbti: str
    message: str

class ChatRequestDto(BaseModel):
    gree_id: int
    message: str