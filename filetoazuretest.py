from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

# Azure 포털에서 확인한 Storage 계정 이름과 접근 키 또는 SAS 토큰을 사용하여 BlobServiceClient 인스턴스 생성
connect_str = '여기에_접근_문자열_입력'
blob_service_client = BlobServiceClient.from_connection_string(connect_str)

# 컨테이너 이름과 업로드할 파일의 경로 설정
container_name = '여기에_컨테이너_이름_입력'
file_path = '여기에_업로드할_파일의_로컬_경로_입력'
blob_name = '업로드될_파일.png'  # Azure Storage에 저장될 파일 이름

# 컨테이너 클라이언트 가져오기
container_client = blob_service_client.get_container_client(container_name)

# BlobClient 인스턴스 생성 및 파일 업로드
blob_client = container_client.get_blob_client(blob_name)
with open(file_path, 'rb') as data:
    blob_client.upload_blob(data)
