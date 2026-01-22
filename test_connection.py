import socket
import time

# Agent PC에서 실행 (172.23.122.102 주소의 보안 PC로 연결 시도)
HOST = '172.23.122.102'
PORT = 9999

try:
    print(f"🔗 {HOST}:{PORT}에 연결 시도...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)  # 5초 타임아웃
    sock.connect((HOST, PORT))
    
    print("✅ 연결 성공!")
    
    # 테스트 명령 전송
    test_command = "CLICK"
    print(f"📤 명령 전송: {test_command}")
    sock.sendall(test_command.encode('utf-8'))
    
    time.sleep(1)
    sock.close()
    print("✅ 전송 완료")
    
except ConnectionRefusedError:
    print("❌ 연결 거부됨 - receiver.py가 실행 중이지 않음")
except socket.timeout:
    print("❌ 타임아웃 - 보안 PC가 응답하지 않음")
except Exception as e:
    print(f"❌ 에러: {e}")
