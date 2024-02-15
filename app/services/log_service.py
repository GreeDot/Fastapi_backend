# services/log_service.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.crud.crud_log import (create_log as crud_create_log,
                          get_log as crud_get_log,
                          get_logs as crud_get_logs,
                          update_log as crud_update_log,
                          delete_log as crud_delete_log)
from app.schemas.LogDto import CreateLogDto
from app.models.models import Log
from sqlalchemy.future import select

async def create_log_service(db: AsyncSession, log_dto: CreateLogDto) -> Log:
    db_log = await crud_create_log(db, log_dto.gree_id, log_dto.log_type, log_dto.content)
    return db_log

async def get_log_service(db: AsyncSession, log_id: int) -> Optional[Log]:
    db_log = await crud_get_log(db, log_id)
    if db_log is None:
        raise HTTPException(status_code=404, detail="Log not found")
    return db_log

async def get_logs_service(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Log]:
    db_logs = await crud_get_logs(db, skip, limit)
    return db_logs

async def delete_log_service(db: AsyncSession, log_id: int) -> Optional[Log]:
    db_log = await crud_delete_log(db, log_id)
    if db_log is None:
        raise HTTPException(status_code=404, detail="Log not found")
    return db_log

async def get_logs_by_gree_service(db: AsyncSession, gree_id: int):
    async with db as session:
        result = await session.execute(select(Log).where(Log.gree_id == gree_id))
        logs = result.scalars().all()
        return logs
    