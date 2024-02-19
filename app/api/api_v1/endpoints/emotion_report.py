from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.models import EmotionReport

router = APIRouter()

@router.get("/")
async def get_emotion_reports(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(EmotionReport).options(selectinload(EmotionReport.emotion_details))
    )
    reports = result.scalars().all()
    return reports

@router.get("/{emotion_report_id}")
async def get_emotion_report(emotion_report_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(EmotionReport).options(selectinload(EmotionReport.emotion_details))
        .where(EmotionReport.id == emotion_report_id)
    )
    report = result.scalars().first()
    if report is None:
        raise HTTPException(status_code=404, detail="EmotionReport not found")
    return report

@router.delete("/{emotion_report_id}")
async def delete_emotion_report(emotion_report_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(EmotionReport).where(EmotionReport.id == emotion_report_id)
    )
    report = result.scalars().first()
    if report is None:
        raise HTTPException(status_code=404, detail="EmotionReport not found")
    await db.delete(report)
    await db.commit()
    return {"message": "EmotionReport deleted"}


@router.get("/by-gree/{gree_id}")
async def get_emotion_report_by_greeid(gree_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(EmotionReport).options(selectinload(EmotionReport.emotion_details))
        .where(EmotionReport.gree_id == gree_id)
    )
    report = result.scalars().all()
    if not report:
        raise HTTPException(status_code=404, detail="EmotionReport not found for given gree_id")
    return report
