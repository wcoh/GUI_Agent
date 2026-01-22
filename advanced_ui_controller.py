"""
고급 UI 제어 및 상호작용 모듈
"""
import streamlit as st
from typing import Dict, Tuple


class AdvancedUIController:
    """분석 결과 기반 고급 UI 제어"""
    
    @staticmethod
    def render_analysis_sidebar(analysis: Dict):
        """분석 결과를 사이드바에 표시"""
        with st.sidebar:
            st.markdown("### 📊 분석 정보")
            
            if analysis and analysis.get('success'):
                elements = analysis.get('elements', [])
                text_blocks = analysis.get('text_blocks', [])
                
                # 탭 구성
                tab1, tab2 = st.tabs(["🎯 요소", "📝 텍스트"])
                
                with tab1:
                    st.subheader(f"인식된 요소: {len(elements)}")
                    
                    if elements:
                        for i, elem in enumerate(elements, 1):
                            with st.expander(f"{i}. {elem.get('type', 'unknown').upper()} - {elem.get('label', 'N/A')[:20]}"):
                                st.markdown(f"**유형**: {elem.get('type')}")
                                st.markdown(f"**라벨**: {elem.get('label', 'N/A')}")
                                st.markdown(f"**신뢰도**: {elem.get('confidence', 0):.2%}")
                                st.markdown(f"**위치**: {elem.get('center', (0, 0))}")
                                st.markdown(f"**설명**: {elem.get('description', 'N/A')}")
                    else:
                        st.info("인식된 요소 없음")
                
                with tab2:
                    st.subheader(f"인식된 텍스트: {len(text_blocks)}")
                    
                    if text_blocks:
                        for i, text_block in enumerate(text_blocks, 1):
                            st.markdown(f"**{i}**. {text_block.get('text', 'N/A')} (신뢰도: {text_block.get('confidence', 0):.2%})")
                    else:
                        st.info("인식된 텍스트 없음")
                
                analysis_time = analysis.get('analysis_time', 0)
                st.markdown(f"**분석 시간**: {analysis_time:.3f}초")
            else:
                st.warning("분석 데이터 없음")
    
    @staticmethod
    def get_action_command(analysis: Dict, user_intent: str) -> str or None:
        """
        사용자 의도와 분석 결과를 기반으로 액션 명령 생성
        
        Args:
            analysis: 화면 분석 결과
            user_intent: 사용자 의도 ("신청" "취소" "확인" 등)
            
        Returns:
            실행할 명령어 또는 None
        """
        if not analysis or not analysis.get('success'):
            return None
        
        # 의도별 버튼 찾기
        intent_map = {
            "신청": ["신청", "accept", "submit", "확인"],
            "취소": ["취소", "cancel", "close", "돌아가기"],
            "확인": ["확인", "ok", "yes"],
            "다음": ["다음", "next", "계속"],
        }
        
        target_labels = intent_map.get(user_intent, [])
        
        for element in analysis.get('elements', []):
            label = element.get('label', '').lower()
            if any(target in label for target in target_labels):
                cx, cy = element.get('center', (0, 0))
                return f"CLICK:{cx},{cy}"
        
        return None


class SmartCommandBuilder:
    """자동 명령 빌더"""
    
    @staticmethod
    def build_workflow_command(steps: list) -> str:
        """
        여러 스텝을 하나의 워크플로우로 변환
        
        Args:
            steps: [{"action": "click", "target": "신청"}, ...]
            
        Returns:
            워크플로우 명령어
        """
        commands = []
        for step in steps:
            action = step.get('action')
            
            if action == 'click':
                commands.append(f"CLICK:{step.get('target')}")
            elif action == 'type':
                commands.append(f"TYPE:{step.get('text')}")
            elif action == 'wait':
                commands.append(f"WAIT:{step.get('duration', 1)}")
            elif action == 'screenshot':
                commands.append("SCREENSHOT")
        
        return ";".join(commands)


if __name__ == "__main__":
    # 테스트용 더미 데이터
    dummy_analysis = {
        'success': True,
        'elements': [
            {
                'type': 'button',
                'label': '신청',
                'confidence': 0.95,
                'center': (200, 100),
                'description': '버튼: 신청'
            }
        ],
        'text_blocks': [
            {
                'text': '유연근무 신청',
                'confidence': 0.92
            }
        ],
        'analysis_time': 0.25
    }
    
    # UI 렌더링 테스트
    controller = AdvancedUIController()
    # controller.render_analysis_sidebar(dummy_analysis)
