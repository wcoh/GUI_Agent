# OmniParser V2 가중치 다운로드 가이드

## 📥 빠른 설정

### 1단계: OmniParser 가중치 다운로드

```powershell
cd D:\agent\agent_MVP\omniparser

# HuggingFace CLI 설치 (처음 한번만)
pip install huggingface-hub

# 가중치 다운로드
# Option 1: PowerShell에서 직접 실행
$files = @(
    "icon_detect/train_args.yaml",
    "icon_detect/model.pt",
    "icon_detect/model.yaml",
    "icon_caption/config.json",
    "icon_caption/generation_config.json",
    "icon_caption/model.safetensors"
)

foreach ($f in $files) {
    huggingface-cli download microsoft/OmniParser-v2.0 "$f" --local-dir weights
}

# 폴더명 변경
Move-Item -Path weights\icon_caption -Destination weights\icon_caption_florence -Force
```

### 2단계: 가중치 확인

다운로드 후 `omniparser\weights` 폴더 구조:

```
weights/
├── icon_detect/
│   ├── train_args.yaml
│   ├── model.pt
│   └── model.yaml
├── icon_caption_florence/
│   ├── config.json
│   ├── generation_config.json
│   └── model.safetensors
```

### 3단계: 애플리케이션 시작

```powershell
cd D:\agent\agent_MVP
streamlit run main.py
```

---

## 🔧 OmniParser 설정

### omniparser_analyzer.py 활성화

가중치를 성공적으로 다운로드한 후, 다음 라인을 수정하여 실제 모델을 사용합니다:

```python
# omniparser_analyzer.py의 _load_model() 메서드에서

# 현재 (데모 모드):
analyzer = ScreenAnalyzer(use_demo_mode=False)  # 자동으로 실제 모델 로드 시도

# 또는 명시적으로:
analyzer = ScreenAnalyzer(use_demo_mode=True)   # 데모 모드 강제
```

---

## 📊 모델 성능

| 메트릭 | OmniParser V2 |
|--------|--------------|
| Screen Spot Pro 정확도 | 39.5% |
| Windows Agent Arena | #1 |
| 처리 속도 | ~1-2초/이미지 |
| GPU 메모리 | ~4-6GB (RTX 3060) |

---

## ⚠️ 문제 해결

### "SSL certificate problem" 에러
이미 해결됨:
```bash
git clone --config http.sslVerify=false https://github.com/microsoft/omniparser.git
```

### "weights 폴더 없음" 경고
```bash
cd omniparser
mkdir -p weights
# 가중치 다운로드 스크립트 실행
```

### 모델 로드 실패
1. 가중치 파일 존재 확인
2. GPU 메모리 확인 (`nvidia-smi`)
3. Python 3.10+ 버전 확인
4. 데모 모드로 UI 테스트 진행

---

## 🚀 데모 모드 vs 실제 모드

### 데모 모드 (현재)
- ✅ UI 테스트 가능
- ✅ 상태 머신 동작 확인
- ✅ 통신 기능 테스트
- ❌ 실제 화면 분석 불가

### 실제 모드 (가중치 다운 후)
- ✅ 실제 UI 요소 탐지
- ✅ 텍스트 인식
- ✅ 아이콘 분류
- ✅ 상호작용 가능 여부 판단
- ⚠️ GPU 필요

---

## 🔗 참고 자료

- [OmniParser GitHub](https://github.com/microsoft/OmniParser)
- [HuggingFace 모델](https://huggingface.co/microsoft/OmniParser-v2.0)
- [OmniParser V2 블로그](https://www.microsoft.com/en-us/research/articles/omniparser-v2-turning-any-llm-into-a-computer-use-agent/)
- [논문](https://arxiv.org/abs/2408.00203)
