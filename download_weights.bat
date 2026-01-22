@echo off
REM OmniParser V2 가중치 다운로드 스크립트

echo ========================================
echo OmniParser V2 가중치 자동 다운로드
echo ========================================

cd /d "%~dp0omniparser"

REM 가중치 디렉토리 생성
if not exist weights (
    mkdir weights
    echo [OK] weights 폴더 생성
)

REM HuggingFace CLI 설치 확인
pip show huggingface-hub >nul 2>&1
if errorlevel 1 (
    echo [INFO] huggingface-hub 설치 중...
    pip install huggingface-hub
)

echo.
echo [INFO] OmniParser V2 가중치 다운로드 시작...
echo [INFO] 이 과정은 5-10분 정도 소요됩니다.
echo.

REM 가중치 다운로드
echo [1/6] icon_detect/train_args.yaml 다운로드 중...
huggingface-cli download microsoft/OmniParser-v2.0 "icon_detect/train_args.yaml" --local-dir weights

echo [2/6] icon_detect/model.pt 다운로드 중...
huggingface-cli download microsoft/OmniParser-v2.0 "icon_detect/model.pt" --local-dir weights

echo [3/6] icon_detect/model.yaml 다운로드 중...
huggingface-cli download microsoft/OmniParser-v2.0 "icon_detect/model.yaml" --local-dir weights

echo [4/6] icon_caption/config.json 다운로드 중...
huggingface-cli download microsoft/OmniParser-v2.0 "icon_caption/config.json" --local-dir weights

echo [5/6] icon_caption/generation_config.json 다운로드 중...
huggingface-cli download microsoft/OmniParser-v2.0 "icon_caption/generation_config.json" --local-dir weights

echo [6/6] icon_caption/model.safetensors 다운로드 중...
huggingface-cli download microsoft/OmniParser-v2.0 "icon_caption/model.safetensors" --local-dir weights

REM 폴더명 변경
echo.
echo [INFO] 폴더 이름 변경 중...
if exist weights\icon_caption (
    rmdir /s /q weights\icon_caption_florence 2>nul
    ren weights\icon_caption icon_caption_florence
    echo [OK] icon_caption -> icon_caption_florence
)

echo.
echo ========================================
echo [완료] OmniParser V2 가중치 설정 완료!
echo ========================================
echo.
echo 다음 단계:
echo 1. cd D:\agent\agent_MVP
echo 2. streamlit run main.py
echo.
pause
