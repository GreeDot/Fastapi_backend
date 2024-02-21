from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Gree
from app.schemas.greeDto import GreeUpdate
import random  # 랜덤 모듈 import

async def update_gree_voice_type(db: AsyncSession, gree_id: int, gree_update: GreeUpdate):
    # MBTI의 첫 글자(E/I)에 따라 활기찬(E) 또는 차분한(I) 결정
    personality_type = 'E' if gree_update.prompt_mbti and gree_update.prompt_mbti.startswith('E') else 'I'

    # 성별에 따른 분류
    gender = gree_update.prompt_gender.upper() if gree_update.prompt_gender else 'N'  # Default to 'N' if None

    # 나이에 따른 분류
    if gree_update.prompt_age is not None:
        if gree_update.prompt_age <= 11:
            age_group = '어린이'
        elif 11 < gree_update.prompt_age <= 17:
            age_group = '청소년'
        else:
            age_group = '청년'
    else:
        age_group = None

    # VoiceTypeEnum에서 적절한 값을 찾기
    voice_type = None
    # 나이 그룹별로 분류된 VoiceTypeEnum 매핑
    voice_type_mapping = {
        ('E', '남자', '어린이'): ['nwoof'],
        ('E', '남자', '청소년'): ['njonghyun'],
        ('E', '남자', '청년'): ['vdonghyun', 'nmammon'],
        ('E', '여자', '어린이'): ['ngaram', 'nmeow'],
        ('E', '여자', '청소년'): ['nihyun'],
        ('E', '여자', '청년'): ['vyuna', 'vhyeri'],
        ('I', '남자', '어린이'): ['nhajun'],
        ('I', '남자', '청소년'): ['njaewook', 'njoonyoung'],
        ('I', '남자', '청년'): ['vdaeseong', 'vian', 'nkyuwon'],
        ('I', '여자', '어린이'): ['vdain', 'ndain'],
        ('I', '여자', '청소년'): ['nminseo', 'nbora', 'njiwon'],
        ('I', '여자', '청년'): ['vgoeun', 'ntiffany'],
    }

    if age_group:
        voice_options = voice_type_mapping.get((personality_type, gender, age_group), [])
        if voice_options:
            voice_type = random.choice(voice_options)  # 선택지 중 하나를 랜덤으로 선택

    if voice_type:
        # gree 객체의 voice_type 업데이트
        stmt = update(Gree).where(Gree.id == gree_id).values(voice_type=voice_type)
        await db.execute(stmt)
        await db.commit()
