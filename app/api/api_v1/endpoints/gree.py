import os
import shutil
from typing import List

from fastapi import Depends, HTTPException, APIRouter, File, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from pydantic import BaseModel

import aiohttp
import aiofiles
import uuid

from app.services.upload_service import upload_file_to_azure, upload_greefile_to_azure, \
    upload_yaml_to_azure_blob, upload_gif_to_azure_blob
from app.api.api_v1.endpoints.user import get_current_user
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


async def download_and_save_file(url: str, destination: str):

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                # 파일을 바이너리 쓰기 모드로 열고 내용을 씁니다.
                async with aiofiles.open(destination, mode='wb') as file:
                    await file.write(await response.read())
            else:
                raise HTTPException(status_code=response.status, detail="Failed to download file.")


@router.post("/greefile/upload/{gree_id}")
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


@router.post("/greefile/upload_yaml/{gree_id}")
async def upload_yaml(
        gree_id: int,
        file: UploadFile = File(...),
        current_user: Member = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    # Gree 객체 조회
    gree = await crud_get_gree_by_id(db, gree_id, user_id=current_user.id)
    if not gree:
        raise HTTPException(status_code=404, detail="Gree not found")

    # 파일을 로컬에 임시 저장
    local_file_path = f"temp/{uuid.uuid4()}.yaml"
    with open(local_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_url = await upload_yaml_to_azure_blob(local_file_path)  # 여기를 수정함

    # GreeFile 객체 생성 및 저장
    gree_file = GreeFile(
        gree_id=gree_id,
        file_type='YAML',
        file_name=file.filename,
        real_name=file_url,
    )
    db.add(gree_file)
    await db.commit()
    await db.refresh(gree_file)

    os.remove(local_file_path)

    return {"message": "YAML file uploaded successfully", "url": file_url}


def create_gif():
    from animated_drawings import render
    # 이 경로는 실제 YAML 파일의 위치에 따라 조정해야 합니다.
    render.start('./animation/char7/export_gif_example.yaml')
    return './temp/video.gif'


@router.post("/create-and-upload-assets/{gree_id}")
async def create_and_upload_assets(
        gree_id: int,
        current_user: Member = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):

    # gree 객체 조회
    gree_result = await db.execute(select(SQLAlchemyGree).where(SQLAlchemyGree.id == gree_id))
    gree = gree_result.scalars().first()
    if not gree:
        raise HTTPException(status_code=404, detail="Gree not found")

    # gree_file 객체에서 yaml 파일 조회
    gree_file_result = await db.execute(
        select(GreeFile)
        .where(GreeFile.gree_id == gree_id, GreeFile.file_type == 'YAML')
    )
    gree_yaml_file = gree_file_result.scalars().first()
    if not gree_yaml_file:
        raise HTTPException(status_code=404, detail="YAML file not found")

    # gree_file 객체에서 img 파일 조회
    gree_img_result = await db.execute(
        select(GreeFile)
        .where(GreeFile.gree_id == gree_id, GreeFile.file_type == 'IMG')
    )
    gree_img_file = gree_img_result.scalars().first()
    if not gree_img_file:
        raise HTTPException(status_code=404, detail="Image file not found")

    # 파일 다운로드 및 저장 경로 설정
    base_path = 'animation/char7'
    os.makedirs(base_path, exist_ok=True)  # 디렉토리가 없으면 생성

    # YAML 파일 다운로드 및 저장
    yaml_file_path = os.path.join(base_path, 'char_cfg.yaml')
    await download_and_save_file(gree_yaml_file.real_name, yaml_file_path)

    # 이미지 파일 다운로드 및 저장
    img_file_path = os.path.join(base_path, 'mask.png')
    await download_and_save_file(gree_img_file.real_name, img_file_path)

    # texture.png (raw_img) 다운로드 및 저장
    texture_file_path = os.path.join(base_path, 'texture.png')
    await download_and_save_file(gree.raw_img, texture_file_path)


    # GIF 생성
    gif_path = create_gif()  # GIF 생성 함수 호출

    # GIF 파일 Azure에 업로드
    uploaded_gif_url = await upload_gif_to_azure_blob(gif_path)  # 비동기 업로드 함수 호출



    return {"message": "Assets and GIF uploaded successfully", "gif_url": uploaded_gif_url}