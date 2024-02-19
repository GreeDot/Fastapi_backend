import os
import uuid
import aiohttp
import openai
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from azure.storage.blob import BlobServiceClient, ContentSettings

from app.crud.crud_gree import crud_get_gree_by_id_only
from app.models.enums import VoiceTypeEnum
from app.schemas.ChatDto import ChatRequestDto
from app.schemas.LogDto import CreateGreeTalkLogDto, CreateUserTalkLogDto
from app.services.log_service import create_greetalk_log_service, create_usertalk_log_service

# chat 테스트를 위한 서비스이다.
async def chat_with_openai_test_service(chat_request):
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
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=1.5,
            top_p=0.7,
            frequency_penalty=0.3,
            presence_penalty=0.1,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": chat_request.message}
            ]
        )
        return completion.choices[0].message.content
    except Exception as exc:
        print(f"An error occurred: {exc}")
        raise HTTPException(status_code=500, detail="An error occurred while processing your request.")



# TODO chat_request에 담겨야 하는 정보:
# 1. gree_id로 gree를 하나 조회한다. ✅
# 2. gree의 정보를 토대로 chat_request에 있는 정보를 채워넣는다. ✅
# 3. 즉 엔드포인트에서 받아야 할 정보는 gree_id, message 이 둘이면 된다. ✅
# 4. gree_id, message로 입력받은 것은 "USER_TALK" Log로 남아야 한다. ✅
# 5. gree_id, message로 출력되는 것은 "GREE_TALK" Log로 데이터베이스에 저장되어야 한다. ✅
# 6. "GREE_TALK" 메시지는 TTS과정을 거쳐야한다.

# 7. TTS를 거친 메시지는 Azure에 저장되어야한다.
# 8. Azure에 저장된 URL은 Log에 저장되어야한다.
# 9. GREE의 성격을 지정할때(Update Gree) Gree객체의 VoiceTypeEnum이 지정되어야한다.
async def chat_with_openai_service(db: AsyncSession, chat_request: ChatRequestDto):
    gree = await crud_get_gree_by_id_only(db, chat_request.gree_id)
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
        
        f"당신은 {gree.prompt_gender}, {gree.prompt_age}살, 이름은 {gree.gree_name}, MBTI는 각각의 성향이 강하게 나타나는 {gree.prompt_mbti}입니다."
    )

    createUserLogDto = CreateUserTalkLogDto(
        gree_id=gree.id,
        log_type='USER_TALK',
        content=chat_request.message
    )

    user_talk = await create_usertalk_log_service(db ,createUserLogDto)

    try:
        completion = openai.ChatCompletion.create(
            model="ft:gpt-3.5-turbo-0613:personal::8sn4jyEw",
            temperature=1.5,
            top_p=0.7,
            frequency_penalty=0.3,
            presence_penalty=0.1,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": chat_request.message}
            ]
        )
        gree_talk= completion.choices[0].message.content

        mp3_path = await text_to_speech(gree.voice_type, gree_talk)
        voice_url_azure= await upload_mp3_azure(mp3_path)

        createGptLogDto = CreateGreeTalkLogDto(
            gree_id=gree.id,
            log_type='GREE_TALK',
            content=gree_talk,
            voice_url=voice_url_azure
        )

        gpt_talk = await create_greetalk_log_service(db ,createGptLogDto)

        return {"user_talk": user_talk, "gpt_talk": gpt_talk}
    except Exception as exc:
        print(f"An error occurred: {exc}")
        raise HTTPException(status_code=500, detail="An error occurred while processing your request.")


async def text_to_speech(voice_type: VoiceTypeEnum, gree_talk: str) -> str:
    url = "https://api.openai.com/v1/audio/speech"
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY') # 환경변수에서 API 키를 가져옵니다.

    payload = {
        "model": "tts-1",
        "input": gree_talk,
        "voice": voice_type.value
    }
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            if response.status == 200:
                content = await response.read()
                
                # 지정된 경로에 디렉토리가 없으면 생성
                dir_path = '/temp/voice_temp/'
                if not os.path.exists(dir_path):
                    os.makedirs(dir_path)
                
                # 파일 저장 경로 변경
                mp3_path = os.path.join(dir_path, f'{voice_type.value}_speech.mp3')
                
                with open(mp3_path, 'wb') as f:
                    f.write(content)
                return mp3_path
            else:
                return "Error: 응답 상태가 200이 아닙니다."
            

async def upload_mp3_azure(mp3_path: str) -> str:
    try:
        container_name = "greefile"
        AZURE_ACCOUNT_KEY = os.getenv("AZURE_ACCOUNT_KEY")
        if not AZURE_ACCOUNT_KEY:
            raise HTTPException(status_code=500, detail="Azure account key is not set in environment variables.")

        connection_string = f"DefaultEndpointsProtocol=https;AccountName=greedotstorage;AccountKey={AZURE_ACCOUNT_KEY};EndpointSuffix=core.windows.net"
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)

        # 파일 이름 추출 및 고유한 파일 이름 생성
        file_name = os.path.basename(mp3_path)
        unique_file_name = f"logVoices/{uuid.uuid4()}_{file_name}"

        blob_client = blob_service_client.get_blob_client(container=container_name, blob=unique_file_name)

        # 파일 업로드
        with open(mp3_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True, content_settings=ContentSettings(content_type='audio/mpeg'))

        # 업로드된 파일의 URL 반환
        return blob_client.url
    except Exception as e:
        print(f"An error occurred while uploading MP3 to Azure: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while uploading MP3 to Azure: {e}")
