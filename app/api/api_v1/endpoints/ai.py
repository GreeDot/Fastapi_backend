from fastapi import APIRouter, Depends, HTTPException
import httpx
from app.database import get_db
from app.schemas.ChatDto import ChatRequestDto, ChatRequestTestDto
from app.schemas.EmotionDto import MakeEmotionReportRequest, MakeEmotionReportResponse, EmotionsRequest, EmotionsResponse, WordCloudRequest, WordCloudResponse
from app.services.emotion_service import save_emotion_report
from app.services.voice_service import chat_with_openai_service, chat_with_openai_test_service
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
SERVER1_BASE_URL = "http://localhost:8001"

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

@router.post("/make-emotion-report/{gree_id}", response_model=MakeEmotionReportResponse)
async def make_emotion_report_api(gree_id: int, request: MakeEmotionReportRequest, db: AsyncSession = Depends(get_db)):
    async with httpx.AsyncClient() as client:
        # 1단계: 감정 예측
        try:
            emotions_response = await client.post(f"{SERVER1_BASE_URL}/predict-emotions", json=request.dict())
            emotions_data = emotions_response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"감정 예측 중 오류 발생: {str(e)}")

        # 2단계: 워드 클라우드 생성을 위한 수정
        try:
            wordcloud_request = {
                "emotions": emotions_data['emotions']  # 'sentences' 대신 'emotions' 사용
            }
            wordcloud_response = await client.post(f"{SERVER1_BASE_URL}/make-wordcloud", json=wordcloud_request)
            wordcloud_data = wordcloud_response.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"워드 클라우드 생성 중 오류 발생: {str(e)}")

        # 'urls' 키가 없는 경우를 처리하기 위한 예외 처리 추가
        if 'urls' not in wordcloud_data:
            raise HTTPException(status_code=500, detail="워드 클라우드 응답에 'urls' 키가 없습니다.")

        await save_emotion_report(gree_id, emotions_data['emotions'], wordcloud_data['urls'], db)

        # 최종 응답 반환
        return MakeEmotionReportResponse(emotions=emotions_data['emotions'], urls=wordcloud_data['urls'])
