from typing import List

from fastapi import Depends, HTTPException, status, APIRouter, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from api.api_v1.endpoints.user import get_current_user
from schemas.gree import GreeUpdate, Gree
from services.upload_service import upload_file_to_azure
from models.models import Member
from core.security import oauth2_scheme
from database import get_db
from pydantic import BaseModel
from crud.crud_gree import crud_get_grees, crud_update_gree, crud_get_gree_by_id, crud_update_gree_status
from crud.crud_user import get_user as crud_get_user

router = APIRouter()


@router.post('/upload-raw-img')
async def upload_raw_img(
        file: UploadFile = File(...),
        current_user: Member = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    file_url = await upload_file_to_azure(file)
    member_id = current_user.id

    gree_data = Gree(
        raw_img=file_url,
        member_id=member_id,
        isFavorite=False,
        status= "activate"
    )
    db.add(gree_data)
    db.flush()  # 비동기 ORM을 사용하는 경우, 해당 메소드의 비동기 버전을 사용해야 할 수 있음
    await db.commit()  # 커밋하여 트랜잭션을 완료

    # 이 시점에서 gree_data 객체는 데이터베이스에 의해 자동으로 생성된 ID를 가짐
    return {"file_url": file_url, "gree_id": gree_data.id, "message": "File uploaded successfully."}


class SuccessMessage(BaseModel):
    message: str


@router.put('/update/{gree_id}', response_model=SuccessMessage)
async def update_gree(gree_id: int, gree_update: GreeUpdate, current_user: Member = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db)):

    user = await crud_get_user(db, current_user.id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    gree = await crud_get_gree_by_id(db, gree_id=gree_id, user_id=user.id)
    if not gree:
        raise HTTPException(status_code=404, detail="Gree not found")

    updated_gree = await crud_update_gree(db, gree_id, gree_update)
    return {"message": "Gree updated successfully"}


@router.get('/view', response_model=List[Gree])
async def read_grees(current_user: Member = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    grees = await crud_get_grees(db, user_id=current_user.id)
    return grees


@router.get('/view/{gree_id}', response_model=Gree)
async def read_gree(gree_id: int, current_user: Member = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user = await crud_get_user(db, current_user.id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    gree = await crud_get_gree_by_id(db, gree_id=gree_id, user_id=user.id)
    if not gree:
        raise HTTPException(status_code=404, detail="Gree not found")

    return gree


@router.put('/disable/{gree_id}', response_model=SuccessMessage)
async def disable_gree(gree_id: int, current_user: Member = Depends(get_current_user),
                       db: AsyncSession = Depends(get_db)):

    user = await crud_get_user(db, current_user.id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    await crud_update_gree_status(db, gree_id=gree_id, user_id=user.id, new_status="DISABLED")

    return {"message": "Gree disabled successfully"}
