# Miniconda를 기반으로 하는 이미지 사용
FROM continuumio/miniconda3

# 환경 변수 설정으로 인터랙티브 모드를 비활성화하여 패키지 설치 중 사용자 입력 대기를 방지
ENV DEBIAN_FRONTEND=noninteractive

# 필요한 라이브러리 설치
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libosmesa6-dev \
    freeglut3-dev \
    libglfw3-dev \
    libgles2-mesa-dev \
    libosmesa6 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /workdir

# Conda 환경 파일 및 현재 디렉토리의 소스 코드를 컨테이너로 복사
COPY . .

# Conda 환경 생성 및 활성화
RUN conda env create -f environment.yml

# Conda 환경을 실행 환경으로 설정
ENV PATH /opt/conda/envs/venv/bin:$PATH

# 환경 변수 설정으로 PyOpenGL이 osmesa를 사용하도록 설정
ENV PYOPENGL_PLATFORM=osmesa

# 컨테이너가 시작될 때 실행할 명령어 설정 (예: main.py 실행)
CMD ["python", "main.py"]
