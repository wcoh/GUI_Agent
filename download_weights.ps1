# OmniParser V2 가중치 다운로드 스크립트 (PowerShell)
# 사용법: .\download_weights.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "OmniParser V2 가중치 자동 다운로드" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 현재 디렉토리 설정
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$omniparserPath = Join-Path $scriptPath "omniparser"

if (-not (Test-Path $omniparserPath)) {
    Write-Host "[ERROR] omniparser 폴더가 없습니다: $omniparserPath" -ForegroundColor Red
    exit 1
}

Set-Location $omniparserPath
Write-Host "[INFO] 현재 위치: $(Get-Location)" -ForegroundColor Green

# 가중치 디렉토리 생성
if (-not (Test-Path "weights")) {
    New-Item -ItemType Directory -Path "weights" | Out-Null
    Write-Host "[OK] weights 폴더 생성" -ForegroundColor Green
}

# HuggingFace CLI 설치 확인
try {
    $output = & huggingface-cli --version 2>&1
    Write-Host "[OK] huggingface-cli 이미 설치됨" -ForegroundColor Green
} catch {
    Write-Host "[INFO] huggingface-hub 설치 중..." -ForegroundColor Yellow
    pip install huggingface-hub
}

Write-Host ""
Write-Host "[INFO] OmniParser V2 가중치 다운로드 시작..." -ForegroundColor Yellow
Write-Host "[INFO] 이 과정은 5-10분 정도 소요됩니다." -ForegroundColor Yellow
Write-Host ""

# 다운로드할 파일 목록
$files = @(
    "icon_detect/train_args.yaml",
    "icon_detect/model.pt",
    "icon_detect/model.yaml",
    "icon_caption/config.json",
    "icon_caption/generation_config.json",
    "icon_caption/model.safetensors"
)

# 각 파일 다운로드
for ($i = 0; $i -lt $files.Count; $i++) {
    $file = $files[$i]
    $num = $i + 1
    Write-Host "[$num/$($files.Count)] $file 다운로드 중..." -ForegroundColor Cyan
    
    try {
        & huggingface-cli download microsoft/OmniParser-v2.0 "$file" --local-dir weights
        Write-Host "[$num/$($files.Count)] 완료" -ForegroundColor Green
    } catch {
        Write-Host "[$num/$($files.Count)] 실패: $_" -ForegroundColor Red
    }
}

# 폴더명 변경
Write-Host ""
Write-Host "[INFO] 폴더 이름 변경 중..." -ForegroundColor Yellow

$iconCaptionPath = Join-Path "weights" "icon_caption"
$iconCaptionFlorencePath = Join-Path "weights" "icon_caption_florence"

if (Test-Path $iconCaptionPath) {
    if (Test-Path $iconCaptionFlorencePath) {
        Remove-Item -Path $iconCaptionFlorencePath -Recurse -Force
    }
    Rename-Item -Path $iconCaptionPath -NewName "icon_caption_florence" -Force
    Write-Host "[OK] icon_caption -> icon_caption_florence" -ForegroundColor Green
}

# 최종 확인
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "[완료] OmniParser V2 가중치 설정 완료!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 가중치 폴더 확인
Write-Host "가중치 폴더 구조:" -ForegroundColor Yellow
if (Test-Path "weights") {
    Get-ChildItem -Path "weights" -Recurse -Depth 2 | Select-Object FullName | ForEach-Object {
        $relativePath = $_.FullName -replace [regex]::Escape((Get-Location).Path + "\"), ""
        Write-Host "  $relativePath" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "다음 단계:" -ForegroundColor Cyan
Write-Host "1. cd D:\agent\agent_MVP" -ForegroundColor Gray
Write-Host "2. streamlit run main.py" -ForegroundColor Gray
Write-Host ""
