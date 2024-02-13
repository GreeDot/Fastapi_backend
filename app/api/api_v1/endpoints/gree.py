import os
from typing import List

from fastapi import Depends, HTTPException, status, APIRouter, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession


from pydantic import BaseModel

import requests
import aiohttp
import aiofiles
import uuid

from app.services.upload_service import upload_file_to_azure, upload_greefile_to_azure
from app.api.api_v1.endpoints.user import get_current_user
from app.models.enums import FileTypeEnum 
from app.schemas.gree import GreeUpdate, Gree
from app.segmentation import segmentImage
from app.models.models import Member, GreeFile
from app.models.models import Gree as SQLAlchemyGree
from app.crud.crud_gree import crud_get_grees, crud_update_gree, crud_get_gree_by_id, crud_update_gree_status
from app.crud.crud_user import get_user as crud_get_user
from app.database import get_db

router = APIRouter()

@router.post('/upload-raw-img')
async def upload_raw_img(
        file: UploadFile = File(...),
        current_user: Member = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    file_url = await upload_file_to_azure(file)
    member_id = current_user.id

    gree_data = SQLAlchemyGree(
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



async def download_image_async(image_url: str, local_file_path: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as response:
            if response.status == 200:
                f = await aiofiles.open(local_file_path, mode='wb')
                await f.write(await response.read())
                await f.close()
            else:
                raise Exception(f"Failed to download image. Status code: {response.status}")


@router.post("/greefile/upload")
async def upload_gree_file(
        gree_id: int,
        current_user: Member = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    gree = await crud_get_gree_by_id(db, gree_id=gree_id, user_id=current_user.id)
    if not gree:
        raise HTTPException(status_code=404, detail="Gree not found")

    # 원본 이미지 URL 추출
    original_image_url = gree.raw_img

    # 원본 이미지 다운로드 경로 설정
    local_original_image_path = f"temp/{uuid.uuid4()}.png"

    # 원본 이미지 다운로드
    await download_image_async(original_image_url, local_original_image_path)

    processed_image_path = segmentImage(local_original_image_path, 'temp/')

    # 처리된 이미지를 Azure에 업로드하고, 결과 URL을 GreeFile에 저장
    uploaded_urls = []
    for image_path in processed_image_path:
        file_name = f"{uuid.uuid4()}.png"
        uploaded_url = await upload_greefile_to_azure(image_path)
        uploaded_urls.append(uploaded_url)

        new_gree_file = GreeFile(
            gree_id=gree_id,
            file_type="img",
            file_name=file_name,
            real_name=uploaded_url
        )
        db.add(new_gree_file)
        await db.commit()
        await db.refresh(new_gree_file)

    # 임시 파일 삭제
    os.remove(local_original_image_path)

    return {"message": "Files uploaded successfully", "urls": uploaded_urls}