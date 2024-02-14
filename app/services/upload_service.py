import cv2
import uuid
from azure.storage.blob import BlobServiceClient, ContentSettings
from fastapi import UploadFile, HTTPException
from io import BytesIO
import yaml
import os

from select import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Gree, GreeFile

from tempfile import NamedTemporaryFile

async def upload_file_to_azure(file: UploadFile) -> str:
    container_name = "greefile"
    AZURE_ACCOUNT_KEY = os.getenv("AZURE_ACCOUNT_KEY")
    connection_string = f'DefaultEndpointsProtocol=https;AccountName=greedotstorage;AccountKey={AZURE_ACCOUNT_KEY};EndpointSuffix=core.windows.net'

    # 파일 내용을 임시 파일에 저장
    with NamedTemporaryFile(delete=False) as temp_file:
        contents = await file.read()
        temp_file.write(contents)
        temp_file.seek(0)  # 파일 읽기 위치를 시작 위치로 이동

        # OpenCV를 사용하여 이미지 읽기
        image = cv2.imread(temp_file.name)

    # 리사이즈할 새로운 너비, 비율에 따라 높이 계산
    new_width = 400
    new_height = 400

    # 이미지 리사이즈
    resized_image = cv2.resize(image, (new_width, new_height))

    # 리사이즈된 이미지를 메모리에 인코딩
    _, buffer = cv2.imencode('.png', resized_image)

    # Blob Service 클라이언트 생성 및 Blob 업로드
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=f"upload/{uuid.uuid4()}.png")

    # 인코딩된 이미지 데이터로부터 Blob에 업로드
    blob_client.upload_blob(BytesIO(buffer.tobytes()), overwrite=True, content_settings=ContentSettings(content_type='image/png'))

    return blob_client.url


async def upload_greefile_to_azure(local_file_path: str) -> str:
    container_name = "greefile"
    AZURE_ACCOUNT_KEY = os.getenv("AZURE_ACCOUNT_KEY")
    connection_string = f"DefaultEndpointsProtocol=https;AccountName=greedotstorage;AccountKey={AZURE_ACCOUNT_KEY};EndpointSuffix=core.windows.net"

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    # 파일 이름은 로컬 파일 경로에서 추출
    file_name = os.path.basename(local_file_path)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=f"upload/{uuid.uuid4()}")

    # 로컬 파일을 읽어서 Azure에 업로드
    with open(local_file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True, content_settings=ContentSettings(content_type='image/png'))

    return blob_client.url


async def upload_yaml_to_azure_blob(local_file_path: str) -> str:
    container_name: str = "greefile"
    AZURE_ACCOUNT_KEY = os.getenv("AZURE_ACCOUNT_KEY")

    connection_string = f"DefaultEndpointsProtocol=https;AccountName=greedotstorage;AccountKey={AZURE_ACCOUNT_KEY};EndpointSuffix=core.windows.net"

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    file_name = os.path.basename(local_file_path)
    unique_file_name = f"{uuid.uuid4()}_{file_name}"

    blob_client = blob_service_client.get_blob_client(container=container_name, blob=unique_file_name)

    with open(local_file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True,
                                content_settings=ContentSettings(content_type='application/x-yaml'))

    # 업로드된 파일의 URL 반환
    blob_url = blob_client.url
    return blob_url