from fastapi import Depends, HTTPException, status, APIRouter, File, UploadFile
from sqlalchemy.orm import Session
from api.api_v1.endpoints.user import get_current_user
from database import get_db
from models.models import Gree, Member
from services.upload_service import upload_file_to_azure

router = APIRouter()

@router.post('/upload-raw-img')
async def upload_raw_img(
    file: UploadFile = File(...),
    current_user: Member = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    file_url = await upload_file_to_azure(file)
    member_id = current_user.id

    gree_data = Gree(
        raw_img=file_url,
        member_id=member_id,
        isFavorite=False,
        status="active"
    )
    db.add(gree_data)
    db.flush()  # 비동기 ORM을 사용하는 경우, 해당 메소드의 비동기 버전을 사용해야 할 수 있음
    await db.commit()  # 커밋하여 트랜잭션을 완료

    # 이 시점에서 gree_data 객체는 데이터베이스에 의해 자동으로 생성된 ID를 가짐
    return {"file_url": file_url, "gree_id": gree_data.id, "message": "File uploaded successfully."}

