from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
from app.schemas.ChatDto import ChatRequestDto, ChatRequestTestDto
from app.services.ai_service import chat_with_openai_service, chat_with_openai_test_service
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post("/chat-test")
async def chat_with_openai(chat_request: ChatRequestTestDto):
    try:
        user_response = await chat_with_openai_test_service(chat_request)
    except HTTPException as exc:
        raise exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
 
    return {"user_response": user_response}


@router.post("/chat")
async def chat_with_openai(chat_request: ChatRequestDto, db: AsyncSession = Depends(get_db)):
    try:
        response = await chat_with_openai_service(db, chat_request)
    except HTTPException as exc:
        raise exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    return {"chat_response": response}
