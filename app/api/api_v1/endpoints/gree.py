from fastapi import Depends, HTTPException, status, APIRouter, File, UploadFile
from sqlalchemy.orm import Session
from app.api.api_v1.endpoints.user import get_current_user
from app.database import get_db
from app.models.models import Gree, Member
from services.upload_service import upload_file_to_azure

router = APIRouter()

@router.post('/upload-raw-img')
async def upload_raw_img(
    file: UploadFile = File(...),
    current_user: Member = Depends(get_current_user),  # Member 객체를 직접 받음
    db: Session = Depends(get_db)
):
    file_url = await upload_file_to_azure(file)

    # member_id를 Member 객체의 id로부터 직접 얻음
    member_id = current_user.id  # current_user 객체에서 id 속성을 사용

    # Gree 객체 생성 및 데이터베이스에 저장
    gree_data = Gree(
        raw_img=file_url,
        member_id=member_id,  # 여기서는 변환할 필요 없이 사용
        isFavorite=False,
        status="active"
    )
    db.add(gree_data)
    await db.commit()

    return {"file_url": file_url, "message": "File uploaded successfully."}
