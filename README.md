# U+ GUI Agent - OmniParser V2 통합 가이드

## 📋 프로젝트 구조

```
agent_MVP/
├── main.py                      # 메인 Streamlit 애플리케이션
├── omniparser_analyzer.py       # OmniParser V2 화면 분석 모듈
├── advanced_ui_controller.py    # 고급 UI 제어 및 명령 생성
├── requirements.txt             # Python 의존성
├── download_weights.ps1         # OmniParser 가중치 다운로드 (PowerShell)
├── download_weights.bat         # OmniParser 가중치 다운로드 (CMD)
├── SETUP_OMNIPARSER.md          # OmniParser 설정 가이드
├── omniparser/                  # OmniParser V2 저장소
│   ├── weights/                 # 모델 가중치 (다운로드 필요)
│   ├── omnitool/
│   ├── requirements.txt
│   └── ...
└── README.md                    # 이 파일
```

## 🎯 주요 개선사항

### 1. **무한 루프 문제 해결**
```python
# ❌ Before: while cap.isOpened() 루프가 UI를 블로킹
while cap.isOpened():
    ret, frame = cap.read()
    # ...
    time.sleep(0.03)

# ✅ After: 단일 프레임 캡처, Streamlit 자동 갱신 활용
ret, frame = cap.read()
if ret:
    # 프레임 처리
    frame_placeholder.image(frame, channels="RGB", use_container_width=True)
```

### 2. **OmniParser 화면 분석 통합**
```python
# 실시간 화면 분석 (주기적으로 1초마다)
if current_time - st.session_state.last_analysis_time > ANALYSIS_INTERVAL:
    analysis = analyzer.analyze_frame(frame)
    st.session_state.last_analysis = analysis
```

### 3. **분석 결과 시각화**
- 탐지된 UI 요소에 바운딩 박스 표시
- 요소 타입별 다양한 색상 (버튼=초록, 텍스트=노란색, 아이콘=마젠타)
- 신뢰도 점수 표시

### 4. **향상된 로깅**
```python
logger.info(f"화면 분석 완료: {len(analysis.get('elements', []))} 개 요소 인식")
logger.error(f"명령 전송 실패: {command} - {e}")
```

---

## 🚀 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. OmniParser V2 가중치 다운로드 (선택사항)

**데모 모드에서는 이 단계가 필요 없습니다. 실제 화면 분석을 위해서만 필요합니다.**

#### 방법 1: PowerShell 스크립트 (권장)
```powershell
.\download_weights.ps1
```

#### 방법 2: CMD 스크립트
```cmd
download_weights.bat
```

#### 방법 3: 수동 다운로드
```bash
cd omniparser
pip install huggingface-hub

# 가중치 다운로드
huggingface-cli download microsoft/OmniParser-v2.0 "icon_detect/train_args.yaml" --local-dir weights
huggingface-cli download microsoft/OmniParser-v2.0 "icon_detect/model.pt" --local-dir weights
huggingface-cli download microsoft/OmniParser-v2.0 "icon_detect/model.yaml" --local-dir weights
huggingface-cli download microsoft/OmniParser-v2.0 "icon_caption/config.json" --local-dir weights
huggingface-cli download microsoft/OmniParser-v2.0 "icon_caption/generation_config.json" --local-dir weights
huggingface-cli download microsoft/OmniParser-v2.0 "icon_caption/model.safetensors" --local-dir weights

# 폴더명 변경
mv weights/icon_caption weights/icon_caption_florence
```

### 3. 애플리케이션 실행
```bash
streamlit run main.py
```

---

## 📊 ScreenAnalyzer API

### 분석 결과 포맷
```python
{
    'success': bool,
    'elements': [
        {
            'type': 'button' | 'text' | 'icon' | 'image',
            'label': '버튼 텍스트',
            'bbox': (x1, y1, x2, y2),
            'center': (cx, cy),
            'confidence': 0.95,
            'description': '상세 설명'
        },
        ...
    ],
    'text_blocks': [
        {
            'text': '인식된 텍스트',
            'bbox': (x1, y1, x2, y2),
            'confidence': 0.92
        },
        ...
    ],
    'analysis_time': 0.25  # 초
}
```

### 주요 메서드
```python
# 프레임 분석
analysis = analyzer.analyze_frame(frame)

# 분석 결과를 프레임에 시각화
frame = analyzer.draw_analysis_result(frame, analysis)

# 클릭 가능한 요소 추출
clickables = analyzer.get_clickable_elements(analysis)

# 특정 텍스트 찾기
button = analyzer.find_element_by_text(analysis, "신청")
```

---

## 💬 AdvancedUIController API

### 분석 결과 사이드바 표시
```python
AdvancedUIController.render_analysis_sidebar(analysis)
```

### 사용자 의도 기반 명령 생성
```python
command = AdvancedUIController.get_action_command(analysis, "신청")
# Returns: "CLICK:200,100" or None
```

### 워크플로우 빌드
```python
workflow = SmartCommandBuilder.build_workflow_command([
    {"action": "click", "target": "신청"},
    {"action": "wait", "duration": 2},
    {"action": "screenshot"},
])
# Returns: "CLICK:신청;WAIT:2;SCREENSHOT"
```

---

## 🔧 상태 머신 (Demo State)

```
IDLE 
  ↓
  ← "유연근무" 명령 입력
  ↓
SCANNING (2초) → 화면 분석 실행, OmniParser 결과 시각화
  ↓
CENTERING (1.5초) → 화면 중앙에 포인트 표시
  ↓
DRAW_CIRCLE (3.5초) → 원 그리기
  ↓
DRAW_SQUARE (3.5초) → 사각형 그리기
  ↓
FINISHED (2초) → 성공 메시지
  ↓
IDLE
```

---

## 📝 로깅 설정

모든 중요한 이벤트는 로깅됩니다:

```python
# INFO 레벨
logger.info("ScreenAnalyzer 초기화 완료")
logger.info("명령 전송 성공: SCAN")
logger.info("화면 분석 완료: 5 개 요소 인식")

# ERROR 레벨
logger.error("모델 로드 실패: {error}")
logger.error("명령 전송 실패: {command} - {error}")
logger.error("프레임 분석 중 오류: {error}")
```

---

## 🎨 UI 테마

- **배경**: 따뜻한 베이지 톤 (#F2F0E9)
- **타이틀**: U+ 파스텔 핑크 (#F78FB3)
- **테마 칼러**: U+ 마젠타 (230, 0, 126)
- **채팅 패널**: 흰색 배경, 둥근 모서리, 부드러운 그림자

---

## 🔮 향후 개선 사항

### 1. **OmniParser V2 실제 모델 활성화** ⭐
```python
# omniparser_analyzer.py에서 가중치 다운로드 후 활성화
analyzer = ScreenAnalyzer(use_demo_mode=False)
```

현재 상태:
- ✅ 데모 모드: 더미 데이터 반환 (UI 테스트용)
- ⏳ 실제 모드: `weights` 폴더 다운로드 후 활성화 가능

### 2. **마우스 제어 고도화**
- 탐지된 요소에 자동으로 마우스 이동
- 클릭/더블클릭/드래그 동작 추가

### 3. **OCR 통합**
- 텍스트 인식 정확도 향상
- 다국어 지원

### 4. **성능 최적화**
- GPU 가속 활용
- 캐싱 메커니즘
- 배치 처리

### 5. **고급 명령**
- 조건부 실행 (IF/THEN 로직)
- 반복 루프 (FOR 루프)
- 타임아웃 처리

---

## 📞 문제 해결

### "HDMI Signal Lost" 에러
- 캡처보드가 제대로 연결되어 있는지 확인
- `CAMERA_INDEX` 값이 올바른지 확인 (0은 첫 번째 카메라)
- `cv2.CAP_PROP_FRAME_WIDTH`와 `HEIGHT` 값이 카메라 사양과 맞는지 확인

### "OmniParser 모델을 로드할 수 없습니다" 경고
- 현재는 데모 모드로 동작 (정상)
- 실제 모델을 사용하려면:
  1. `download_weights.ps1` 또는 `download_weights.bat` 실행
  2. 가중치 다운로드 완료 후 앱 재시작

### 분석 결과가 없음 (데모 모드)
- 현재는 더미 데이터 반환 (정상)
- 이는 UI 테스트용입니다
- 실제 화면 분석을 원하면 OmniParser 가중치를 다운로드하세요

### 느린 성능
- 분석 주기 (`ANALYSIS_INTERVAL`) 조정 (현재 1.0초)
- 프레임 해상도 감소 (1920x1080 → 1280x720)
- GPU 사용 가능 여부 확인 (`nvidia-smi`)
- CPU만 사용 시 분석 시간 3-5초 소요

### GPU 메모리 부족
```
RuntimeError: CUDA out of memory
```
해결방법:
- 더 작은 배치 크기 사용
- 타 애플리케이션 종료
- GPU 메모리 정리: `torch.cuda.empty_cache()`

---

## 📚 참고 자료

- [Streamlit 문서](https://docs.streamlit.io/)
- [OpenCV 문서](https://docs.opencv.org/)
- [OmniParser GitHub](https://github.com/microsoft/omniparser)
- [Socket 프로그래밍](https://docs.python.org/3/library/socket.html)

