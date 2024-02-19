from app.models.models import EmotionDetail, EmotionReport
from sqlalchemy.ext.asyncio import AsyncSession

async def save_emotion_report(gree_id: int, emotions: dict, urls: dict, db: AsyncSession):
    new_report = EmotionReport(gree_id=gree_id)
    db.add(new_report)
    await db.flush()  # EmotionReport의 ID를 얻기 위해 flush

    for emotion, sentences in emotions.items():
        wordcloud_url = urls.get(emotion)
        new_detail = EmotionDetail(
            emotion_report_id=new_report.id,
            emotion_type=emotion,
            sentences=sentences,
            wordcloud_url=wordcloud_url
        )
        db.add(new_detail)

    await db.commit()  # 모든 변경사항을 DB에 커밋
