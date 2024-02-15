from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from sqlalchemy.future import select
from app.models.models import Log  # 모델 파일 경로에 따라 수정해야 할 수 있음

# 로그 생성
async def create_log(db: AsyncSession, gree_id: int, log_type, content: str, voice_url: str):
    db_log = Log(
        gree_id=gree_id,
        log_type=log_type,
        content=content,
        voice_url=voice_url,
        register_at=datetime.now()
    )
    db.add(db_log)
    await db.commit()
    await db.refresh(db_log)
    return db_log

# 로그 읽기 (단일 로그)
async def get_log(db: AsyncSession, log_id: int):
    result = await db.execute(select(Log).filter(Log.id == log_id))
    return result.scalars().first()

# 로그 읽기 (모든 로그)
async def get_logs(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Log).offset(skip).limit(limit))
    return result.scalars().all()

# 로그 업데이트
async def update_log(db: AsyncSession, log_id: int, gree_id: int, log_type, content: str):
    result = await db.execute(select(Log).filter(Log.id == log_id))
    db_log = result.scalars().first()
    if db_log is None:
        return None
    db_log.gree_id = gree_id
    db_log.log_type = log_type
    db_log.content = content
    await db.commit()
    await db.refresh(db_log)
    return db_log

# 로그 삭제
async def delete_log(db: AsyncSession, log_id: int):
    result = await db.execute(select(Log).filter(Log.id == log_id))
    db_log = result.scalars().first()
    if db_log is None:
        return None
    await db.delete(db_log)
    await db.commit()
    return db_log