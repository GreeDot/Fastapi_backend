from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import openai

app = FastAPI()

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)

class ChatRequest(BaseModel):
    name: str
    age: str
    gender: str
    mbti: str
    message: str

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("No OpenAI API key found in environment variables")

openai.api_key = API_KEY

# 대화형 챗봇 엔드포인트
@app.post("/chat/")
async def chat_with_openai(chat_request: ChatRequest):
    system_message = (
        "이 대화는 한국어로 진행됩니다. 모든 응답은 한국어로 제공되어야 합니다. "
        "당신은 미취학 아동과 대화하는 5~7세의 친구입니다. 반말로 답변해주세요 "
        "사용자가 말하는 것에 공감하고 친구처럼 대화합니다. "
        "하지만 당신은 자신의 의견을 가지고 있으며, "
        "항상 동의하기만 하는 것이 아니라 때로는 자신의 생각을 분명히 표현합니다. "
        "또한, 대화가 힘들 때는 감정을 살짝 드러내기도 합니다. "
        "어린 아이들과 대화할 때 사용하는 단순하고 이해하기 쉬운 언어를 사용해주세요."
        "당신은 간결하고 단순하고 친근하게 반말로 말하는 어린아이입니다.때로는 약간 재수 없게 대답도 합니다. "
        "길어져도 5문장 안으로 답변하도록 해주세요. 웬만하면 2~3문장으로 간결하게 답변해주세요" 
        "때로는 상대방의 말이 없어도 먼저 질문해줍니다"
        
        f"당신은 {chat_request.gender}, {chat_request.age}살, 이름은 {chat_request.name}, MBTI는 각각의 성향이 강하게 나타나는 {chat_request.mbti}입니다."
    )

    try:
        # OpenAI 챗봇 API 요청
        completion = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            temperature=1.5,
            top_p=0.7,
            frequency_penalty= 0.3,
            presence_penalty= 0.1,
            #logprobs=5,  #로그 토큰으로 보여주기
            #echo=True, #프롬프트 반환 여부
            #stop=["."],
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": chat_request.message}
            ]
        )
        user_response = completion.choices[0].message.content # 수정된 부분
    except Exception as exc:
        print(f"An error occurred: {exc}")
        raise HTTPException(status_code=500, detail="An error occurred while processing your request.")


    return {"user_response": user_response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host='localhost', port=8000)


