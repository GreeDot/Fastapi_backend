import os

from azure.storage.blob import BlobServiceClient, BlobClient, ContentSettings
from fastapi import UploadFile
import shutil
import uuid



async def upload_file_to_azure(file: UploadFile) -> str:
    container_name = "greefile"
    AZURE_ACCOUNT_KEY = os.getenv("AZURE_ACCOUNT_KEY")
    connection_string = f'DefaultEndpointsProtocol=https;AccountName=greedotstorage;AccountKey={AZURE_ACCOUNT_KEY};EndpointSuffix=core.windows.net'

    temp_dir = "temp"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)  # temp 폴더가 없으면 생성
    temp_file_path = f"{temp_dir}/{uuid.uuid4()}.png"

    with open(temp_file_path, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=f"upload/{uuid.uuid4()}.png")

    with open(temp_file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True, content_settings=ContentSettings(content_type='image/png'))

    os.remove(temp_file_path)
    return blob_client.url