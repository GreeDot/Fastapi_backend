import uuid

import aiofiles
import httpx
import asyncio

from azure.storage.blob import ContentSettings
from azure.storage.blob.aio import BlobServiceClient
from typing import List
import os

from fastapi import HTTPException

MID_API_KEY = os.getenv('MID_API_KEY')
container_name = "greefile"
AZURE_ACCOUNT_KEY = os.getenv("AZURE_ACCOUNT_KEY")
connection_string = f'DefaultEndpointsProtocol=https;AccountName=greedotstorage;AccountKey={AZURE_ACCOUNT_KEY};EndpointSuffix=core.windows.net'
promptDict = {
    1: """
    **normal**
    please make cute This picture was painted by a child. 
    Please change this picture a little bit more cute. 
    I want to keep most of the original. 
    Arms and legs must be in the form of characters. 
    Please don't put your face and body in. I just wish I had one character. 
    And the parts other than the character outline must be a white background, so please make this important. 
    transparent png download, 
    --no background, shadow, surrounding friend, surrounding objects
    --quality 0.5
    """,
    2: """
    **sketch**
    in the style of childs drawing, 
    transparent png download, 
    simple, 
    cute and colorful, 
    hd,
    full body shot,
    wearing shoes,
    --no background, shadow, surrounding friend, surrounding objects
    --quality 0.5
    --stylize 50
    """,
    3: """
    **anime**
    anime,
    transparent png download, 
    simple, 
    cute and colorful, 
    hd,
    full body shot,
    wearing shoes,
    --no background, shadow, surrounding friend, surrounding objects
    --quality 0.5
    """,
    4: """
    **dizney**
    Disney style,
    3d animation, 
    transparent png download, 
    simple, 
    cute and colorful, 
    hd,
    full body shot,
    wearing shoes,
    --no background, shadow, surrounding friend, surrounding objects
    """
}

async def create_image(promptSelect: int, raw_img_url: str) -> dict:
    prompt = raw_img_url + ' '
    prompt += promptDict[promptSelect]
    
    headers = {
        'Authorization': f'Bearer {MID_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {"prompt": prompt}
    async with httpx.AsyncClient() as client:
        response = await client.post('https://cl.imagineapi.dev/items/images/', json=data, headers=headers)
        return response.json()

async def check_image_status(image_id: str) -> list:
    headers = {'Authorization': f'Bearer {MID_API_KEY}'}
    async with httpx.AsyncClient() as client:
        while True:
            response = await client.get(f'https://cl.imagineapi.dev/items/images/{image_id}', headers=headers)
            data = response.json()
            if data['data']['status'] == 'completed':
                if 'upscaled_urls' in data['data']:
                    return data['data']['upscaled_urls']
                else:
                    # Handle case where 'upscaled_urls' is missing even though status is 'completed'
                    raise HTTPException(status_code=500, detail="Image creation completed but did not return URLs.")
            elif data['data']['status'] == 'failed':
                # Handle failed image creation
                raise HTTPException(status_code=500, detail="Image creation failed.")
            await asyncio.sleep(5)  # Polling interval


async def upload_images_to_azure(image_paths: List[str]) -> List[str]:
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    uploaded_urls = []
    async with blob_service_client:
        for image_path in image_paths:
            filename = os.path.basename(image_path) or str(uuid.uuid4())
            blob_name = f"upload/{filename}.png"
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

            async with aiofiles.open(image_path, 'rb') as file:
                data = await file.read()

            await blob_client.upload_blob(data, overwrite=True, content_settings=ContentSettings(content_type='image/png'))
            uploaded_urls.append(blob_client.url)
    return uploaded_urls
