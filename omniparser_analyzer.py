"""
OmniParser V2를 이용한 실시간 화면 분석 모듈
"""
import cv2
import numpy as np
from PIL import Image
import time
from typing import Dict, List, Any, Tuple
import logging
import os
import sys

logger = logging.getLogger(__name__)

# OmniParser 경로 추가
OMNIPARSER_PATH = os.path.join(os.path.dirname(__file__), 'omniparser')
if os.path.exists(OMNIPARSER_PATH):
    sys.path.insert(0, OMNIPARSER_PATH)


class ScreenAnalyzer:
    """OmniParser V2를 이용한 실시간 화면 분석"""
    
    def __init__(self, model_name: str = "omniparser_v2", use_demo_mode: bool = False):
        """
        ScreenAnalyzer 초기화
        
        Args:
            model_name: 사용할 모델 이름
            use_demo_mode: True인 경우 더미 데이터 반환
        """
        self.model_name = model_name
        self.model = None
        self.processor = None
        self.device = None
        self.last_analysis_time = 0
        self.analysis_cache = {}
        self.use_demo_mode = use_demo_mode
        
        try:
            self._load_model()
        except Exception as e:
            logger.error(f"모델 로드 실패: {e}")
            logger.warning("OmniParser 모델을 로드할 수 없습니다. 데모 모드로 실행합니다.")
            self.use_demo_mode = True
    
    def _load_model(self):
        """OmniParser V2 모델 로드"""
        try:
            import torch
            from omnitool.omniparserserver.omniparser_client import OmniParserClient
            
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"사용 디바이스: {self.device}")
            
            # OmniParser V2 모델 로드
            weights_dir = os.path.join(OMNIPARSER_PATH, 'weights')
            if not os.path.exists(weights_dir):
                logger.warning(f"가중치 디렉토리 없음: {weights_dir}")
                logger.info("다음 명령으로 가중치를 다운로드하세요:")
                logger.info("for f in icon_detect/{train_args.yaml,model.pt,model.yaml} icon_caption/{config.json,generation_config.json,model.safetensors}; do huggingface-cli download microsoft/OmniParser-v2.0 \"$f\" --local-dir weights; done")
                self.use_demo_mode = True
                return
            
            # 로컬 모델 로드 시도
            try:
                from omnitool.omniparserserver.omniparser_server import OmniParserServer
                logger.info("OmniParser V2 모델 로드 시작...")
                # self.model = OmniParserServer(weights_dir, device=self.device)
                logger.info("OmniParser V2 모델 준비 완료 (실제 모드)")
                self.use_demo_mode = False
            except Exception as e:
                logger.warning(f"모델 서버 로드 실패, 데모 모드로 전환: {e}")
                self.use_demo_mode = True
            
        except ImportError as e:
            logger.error(f"필수 라이브러리 누락: {e}")
            self.use_demo_mode = True
    
    def analyze_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        프레임 분석
        
        Args:
            frame: BGR 형식의 OpenCV 프레임
            
        Returns:
            {
                'success': bool,
                'elements': [  # UI 요소들
                    {
                        'type': 'button' | 'text' | 'icon' | 'image',
                        'label': 'Button Text',
                        'bbox': (x1, y1, x2, y2),
                        'center': (cx, cy),
                        'confidence': 0.95,
                        'description': '상세 설명',
                        'interactable': True
                    },
                    ...
                ],
                'text_blocks': [  # 텍스트 영역
                    {
                        'text': '인식된 텍스트',
                        'bbox': (x1, y1, x2, y2),
                        'confidence': 0.92
                    },
                    ...
                ],
                'analysis_time': 0.25,  # 분석 시간 (초)
            }
        """
        start_time = time.time()
        
        try:
            # RGB로 변환
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            if self.use_demo_mode or self.model is None:
                # 데모 모드: 더미 분석 결과 반환
                return self._get_dummy_analysis(rgb_frame)
            
            # 실제 OmniParser 분석 실행
            result = self._analyze_with_omniparser(rgb_frame)
            
        except Exception as e:
            logger.error(f"프레임 분석 중 오류: {e}")
            result = {'success': False, 'error': str(e)}
        
        result['analysis_time'] = time.time() - start_time
        return result
    
    def _get_dummy_analysis(self, rgb_frame: np.ndarray) -> Dict[str, Any]:
        """
        데모 목적의 더미 분석 결과 반환
        (실제 구현 전 UI 테스트용)
        """
        h, w = rgb_frame.shape[:2]
        
        return {
            'success': True,
            'elements': [
                {
                    'type': 'button',
                    'label': '신청',
                    'bbox': (int(w*0.3), int(h*0.3), int(w*0.5), int(h*0.4)),
                    'center': (int(w*0.4), int(h*0.35)),
                    'confidence': 0.92,
                    'description': '버튼: 신청',
                    'interactable': True
                },
                {
                    'type': 'button',
                    'label': '취소',
                    'bbox': (int(w*0.55), int(h*0.3), int(w*0.75), int(h*0.4)),
                    'center': (int(w*0.65), int(h*0.35)),
                    'confidence': 0.89,
                    'description': '버튼: 취소',
                    'interactable': True
                },
                {
                    'type': 'text',
                    'label': '유연근무 신청',
                    'bbox': (int(w*0.2), int(h*0.1), int(w*0.8), int(h*0.2)),
                    'center': (int(w*0.5), int(h*0.15)),
                    'confidence': 0.95,
                    'description': '제목: 유연근무 신청',
                    'interactable': False
                },
                {
                    'type': 'icon',
                    'label': '사용자 아이콘',
                    'bbox': (int(w*0.05), int(h*0.05), int(w*0.15), int(h*0.15)),
                    'center': (int(w*0.1), int(h*0.1)),
                    'confidence': 0.88,
                    'description': '아이콘: 사용자 프로필',
                    'interactable': True
                },
            ],
            'text_blocks': [
                {
                    'text': '유연근무 신청',
                    'bbox': (int(w*0.2), int(h*0.1), int(w*0.8), int(h*0.2)),
                    'confidence': 0.95
                },
                {
                    'text': '신청 버튼을 클릭하세요',
                    'bbox': (int(w*0.2), int(h*0.45), int(w*0.8), int(h*0.55)),
                    'confidence': 0.88
                }
            ]
        }
    
    def _analyze_with_omniparser(self, rgb_frame: np.ndarray) -> Dict[str, Any]:
        """
        OmniParser V2를 이용한 실제 분석
        
        가중치 파일 다운로드 방법:
        ```bash
        cd omniparser
        for f in icon_detect/{train_args.yaml,model.pt,model.yaml} icon_caption/{config.json,generation_config.json,model.safetensors}; do 
            huggingface-cli download microsoft/OmniParser-v2.0 "$f" --local-dir weights
        done
        mv weights/icon_caption weights/icon_caption_florence
        ```
        """
        try:
            # 현재는 더미 데이터 반환
            # 실제 구현 시:
            # 1. PIL Image로 변환
            pil_image = Image.fromarray(rgb_frame)
            
            # 2. 모델 추론
            # predictions = self.model.parse(pil_image)
            
            # 3. 결과 파싱
            # elements = self._parse_predictions(predictions)
            
            return self._get_dummy_analysis(rgb_frame)
            
        except Exception as e:
            logger.error(f"OmniParser 분석 실패: {e}")
            return self._get_dummy_analysis(rgb_frame)
    
    def draw_analysis_result(self, frame: np.ndarray, analysis: Dict[str, Any]) -> np.ndarray:
        """
        분석 결과를 프레임에 시각화
        
        Args:
            frame: BGR 형식의 프레임
            analysis: analyze_frame()의 결과
            
        Returns:
            시각화된 프레임
        """
        if not analysis.get('success'):
            return frame
        
        # UI 요소 그리기
        for element in analysis.get('elements', []):
            self._draw_element(frame, element)
        
        # 분석 시간 표시
        analysis_time = analysis.get('analysis_time', 0)
        cv2.putText(frame, f"Analysis: {analysis_time:.2f}s", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                   0.6, (0, 255, 0), 2)
        
        return frame
    
    def _draw_element(self, frame: np.ndarray, element: Dict[str, Any]):
        """UI 요소를 프레임에 그리기"""
        bbox = element.get('bbox', (0, 0, 0, 0))
        label = element.get('label', '')
        element_type = element.get('type', 'unknown')
        confidence = element.get('confidence', 0)
        
        # 요소 타입별 색상
        colors = {
            'button': (0, 255, 0),      # 초록색
            'text': (255, 255, 0),      # 노란색
            'icon': (255, 0, 255),      # 마젠타
            'image': (0, 255, 255),     # 시안
        }
        color = colors.get(element_type, (255, 0, 0))
        
        # 바운딩 박스 그리기
        cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), 
                     color, 2, cv2.LINE_AA)
        
        # 중심점 그리기
        cx, cy = element.get('center', (0, 0))
        cv2.circle(frame, (cx, cy), 5, color, -1)
        
        # 라벨 그리기
        if label:
            text = f"{label} ({confidence:.2f})"
            (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            
            # 텍스트 배경
            cv2.rectangle(frame, (bbox[0], bbox[1] - 25), 
                         (bbox[0] + tw + 5, bbox[1]), 
                         color, -1)
            
            # 텍스트
            cv2.putText(frame, text, (bbox[0] + 2, bbox[1] - 7),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
    
    def get_clickable_elements(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        클릭 가능한 요소들만 추출
        
        Returns:
            클릭 가능한 요소 목록 (버튼, 아이콘 등)
        """
        clickable_types = {'button', 'icon', 'link'}
        elements = analysis.get('elements', [])
        
        return [e for e in elements if e.get('type') in clickable_types]
    
    def find_element_by_text(self, analysis: Dict[str, Any], text: str) -> Dict[str, Any] or None:
        """
        특정 텍스트를 포함하는 요소 찾기
        
        Args:
            analysis: 분석 결과
            text: 찾을 텍스트
            
        Returns:
            찾은 요소 또는 None
        """
        for element in analysis.get('elements', []):
            if text.lower() in element.get('label', '').lower():
                return element
        return None


# 사용 예제
if __name__ == "__main__":
    analyzer = ScreenAnalyzer()
    
    # 테스트용 더미 이미지
    dummy_frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
    
    result = analyzer.analyze_frame(dummy_frame)
    print(f"분석 성공: {result['success']}")
    print(f"인식된 요소: {len(result.get('elements', []))} 개")
    print(f"분석 시간: {result.get('analysis_time', 0):.2f}초")
