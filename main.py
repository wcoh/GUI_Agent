import streamlit as st
import cv2
import numpy as np
import socket
import time
import logging
# OmniParser 관련 임포트가 없다면 주석 처리하거나 더미 클래스를 만드세요.
from omniparser_analyzer import ScreenAnalyzer
from advanced_ui_controller import AdvancedUIController

# --- [사용자 설정] ---
TARGET_IP = '192.168.219.105'  # 보안 PC IP
TARGET_PORT = 9999
CAMERA_INDEX = 0  # 캡처보드 인덱스

# --- [로깅 설정] ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- [페이지 설정] ---
st.set_page_config(layout="wide", page_title="U+ GUI Agent")

# --- [CSS: 스타일링 정의] ---
st.markdown("""
<style>
    /* 1. 전체 앱 배경 */
    .stApp {
        background-color: #F2F0E9;
        color: #333333;
    }

    /* 헤더/푸터 숨김 */
    header, footer {visibility: hidden;}

    /* 2. 레이아웃 조정 */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
        max-width: 100% !important;
    }
    
    /* 3. 오른쪽 채팅 컬럼(패널) 스타일링 */
    /* Streamlit의 st.container(height=...)를 쓰면 구조가 바뀌므로
       단순히 배경과 테두리만 설정합니다. */
    div[data-testid="column"]:nth-of-type(2) {
        background-color: #FFFFFF;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        border: 1px solid #E6E6E6;
        /* 높이 강제 지정 제거 (내부 컨테이너에 맡김) */
    }

    /* 4. 채팅 메시지 텍스트 색상 */
    .stChatMessage p {
        color: #2D2D2D !important;
        font-weight: 500;
    }

    /* 어시스턴트 메시지 배경 투명화 */
    .stChatMessage {
        background-color: transparent !important;
    }

    /* 5. 타이틀 스타일 */
    h3 {
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: 700;
        color: #F78FB3 !important;
        margin-bottom: 1rem;
    }

    /* 입력창 스타일 조정 */
    .stChatInputContainer {
        padding-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)


# --- [통신 함수] ---
def send_command_to_target(command):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3.0)
        sock.connect((TARGET_IP, TARGET_PORT))
        sock.sendall(command.encode('utf-8'))
        sock.close()
        logger.info(f"✅ 명령 전송 성공: {command}")
        return True
    except Exception as e:
        logger.error(f"❌ 명령 전송 실패: {command} - {e}")
        return False


# --- [오버레이 함수] ---
def draw_modern_overlay(frame, x, y, label=None, color=(230, 0, 126)):
    cv2.rectangle(frame, (x - 80, y - 30), (x + 80, y + 30), color, 2, cv2.LINE_AA)
    if label:
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        cv2.rectangle(frame, (x - 80, y - 55), (x - 80 + tw + 10, y - 35), (255, 255, 255), -1)
        cv2.putText(frame, label, (x - 75, y - 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1, cv2.LINE_AA)
    return frame


# --- [세션 초기화] ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "안녕하세요. U+ GUI Agent입니다. 무엇을 도와드릴까요?"}]

if "demo_state" not in st.session_state:
    st.session_state.demo_state = "IDLE"
if "step_start_time" not in st.session_state:
    st.session_state.step_start_time = 0
if "cap" not in st.session_state:
    st.session_state.cap = cv2.VideoCapture(CAMERA_INDEX)
    st.session_state.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    st.session_state.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# 분석기 초기화 (최초 1회)
if "analyzer" not in st.session_state:
    with st.spinner("AI 모델을 로드하는 중입니다..."):
        # use_demo_mode=True로 설정하여 모델 가중치가 없어도 테스트 가능하도록 함
        st.session_state.analyzer = ScreenAnalyzer(use_demo_mode=True)
        logger.info("✅ ScreenAnalyzer 초기화 완료")


# ================= LAYOUT =================
col_screen, col_chat = st.columns([0.75, 0.25], gap="large")

# --- [Right Column: Chat Panel] ---
with col_chat:
    st.markdown("### U+ GUI Agent")  # 타이틀
    st.markdown("---")
    
    # [핵심 변경] st.container(height=...) 사용
    # 높이를 600px(또는 원하는 만큼)로 고정하면, 
    # 내용이 넘칠 때 이 안에서만 스크롤이 생깁니다.
    # border=False로 설정하여 이중 테두리를 방지합니다.
    with st.container(height=600, border=False):
        for msg in st.session_state.messages:
            avatar = "🤖" if msg["role"] == "assistant" else None
            with st.chat_message(msg["role"], avatar=avatar):
                st.markdown(msg["content"])

    # [핵심 변경] st.chat_input은 컨테이너 밖(아래)에 위치
    # 이렇게 하면 메시지 영역은 위에서 스크롤되고, 입력창은 항상 아래에 고정된 것처럼 보입니다.
    if prompt := st.chat_input("명령어를 입력하세요..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        if "유연근무" in prompt:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "화면을 분석하여 **유연근무 신청** 프로세스를 실행합니다."
            })
            st.session_state.demo_state = "SCANNING"
            st.session_state.step_start_time = time.time()
            send_command_to_target("SCAN")
            st.rerun()
        else:
            st.session_state.messages.append({"role": "assistant", "content": "죄송합니다. 정확한 명령을 입력해주세요."})
            st.rerun()


# --- [Left Column: Screen Area] ---
with col_screen:
    st.markdown("### User Screen")
    st.markdown('<div style="border-radius: 10px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">', unsafe_allow_html=True)
    
    frame_placeholder = st.empty()
    cap = st.session_state.cap
    
    if not cap.isOpened():
        cap.open(CAMERA_INDEX)
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            frame_placeholder.error("HDMI Signal Lost")
            break
        
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, _ = frame.shape
        THEME_COLOR = (230, 0, 126)
        current_state = st.session_state.demo_state
        elapsed = time.time() - st.session_state.step_start_time
        
        if current_state == "SCANNING":
            progress = elapsed / 2.0
            if progress < 1.0:
                mouse_x = int(w * progress)
                mouse_y = int(h * progress)
                cv2.line(frame, (0, 0), (mouse_x, mouse_y), THEME_COLOR, 3, cv2.LINE_AA)
                cv2.circle(frame, (mouse_x, mouse_y), 15, THEME_COLOR, -1)
                cv2.putText(frame, "Moving...", (50, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, THEME_COLOR, 2)
                send_command_to_target(f"MOVE:{mouse_x},{mouse_y}")
            else:
                if elapsed > 2.0:
                    st.session_state.demo_state = "FINISHED"
                    st.session_state.step_start_time = time.time()
                    send_command_to_target(f"MOVE:{w},{h}")
                    send_command_to_target("CLICK")
        
        elif current_state == "FINISHED":
            draw_modern_overlay(frame, w // 2, h // 2, "Success", (0, 150, 0))
            if elapsed > 2.0:
                st.session_state.demo_state = "IDLE"
        
        frame_placeholder.image(frame, channels="RGB")
        time.sleep(0.03)

    st.markdown('</div>', unsafe_allow_html=True)