from azure.storage.blob import BlobClient, ContentSettings

# 업로드할 파일의 경로와 Azure Storage에 저장될 파일 이름 설정
file_path = 'uploadtest.png'
blob_url = 'https://greedotstorage.blob.core.windows.net/greefile/uploadtest_blob2.png'
sas_token = 'sp=racwdl&st=2024-02-06T07:49:33Z&se=2024-02-06T15:49:33Z&sv=2022-11-02&sr=c&sig=OJe9fWrT884fdNSXyFrc9y2%2BuJw%2FOUDep78u4zhBq6M%3D'

# BlobClient 인스턴스 생성
blob_client = BlobClient.from_blob_url(blob_url=blob_url, credential=sas_token)

# 파일 업로드 시 Content-Type 설정을 위한 ContentSettings 인스턴스 생성
content_settings = ContentSettings(content_type='image/png')

# 파일 업로드
with open(file_path, 'rb') as data:
    blob_client.upload_blob(data, overwrite=True, content_settings=content_settings)