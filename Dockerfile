# Ubuntu 20.04를 기반 이미지로 사용
FROM python:3.10

# 환경 변수 설정으로 인터랙티브 모드를 비활성화하여 패키지 설치 중 사용자 입력 대기를 방지
ENV DEBIAN_FRONTEND=noninteractive

# Python 설치 및 pip 업그레이드
RUN apt-get update
RUN apt-get install -y python3 python3-pip
RUN pip3 install --upgrade pip

# 작업 디렉토리 설정
WORKDIR /app

# 현재 디렉토리의 requirements.txt와 main.py를 /app으로 복사
COPY . . 

# requirements.txt에 명시된 패키지들 설치
RUN pip3 install -r requirements.txt

# 컨테이너가 시작될 때 main.py 실행
CMD ["python3", "app/main.py"]
