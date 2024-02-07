from fastapi import Depends, HTTPException, status, APIRouter, File, UploadFile
from sqlalchemy.orm import Session
from app.api.api_v1.endpoints.user import get_current_user
from app.database import get_db
from app.models.models import Gree

router = APIRouter()

@router.post('/upload-raw-img')
async def upload_raw_img(
    file: UploadFile = File(...),
    member_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)  # 데이터베이스 세션 의존성 주입
):
    # file_url = await upload_file_to_azure(file)
    file_url = file

    # Gree 객체 생성 및 데이터베이스에 저장
    gree_data = Gree(
        raw_img=file_url,
        member_id=member_id,
        # gree_id, register_id 등 필요한 정보 추가
        isFavorite=False,
        status="active"
    )
    db.add(gree_data)
    db.commit()

    return {"file_url": file_url, "message": "File uploaded successfully."}