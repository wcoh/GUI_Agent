import socket
import pyautogui
import threading
import sys

HOST = '0.0.0.0' 
PORT = 9999

def handle_client(client_socket, addr):
    print(f"🔗 [연결] {addr}", flush=True)
    sys.stdout.flush()
    
    while True:
        try:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                print(f"❌ [종료] {addr} - 데이터 없음", flush=True)
                break
            
            print(f"📨 [수신] {addr}: {data}", flush=True)
            sys.stdout.flush()
            
            if data.startswith("MOVE:"):
                coords = data.split(":")[1].split(",")
                x, y = int(coords[0]), int(coords[1])
                print(f"  → 마우스 이동: ({x}, {y})", flush=True)
                pyautogui.moveTo(x, y, duration=0.5)
                print(f"  ✅ 완료", flush=True)
                
            elif data == "CLICK":
                print(f"  → 클릭 실행", flush=True)
                pyautogui.click()
                print(f"  ✅ 완료", flush=True)
                
            elif data.startswith("TYPE:"):
                text = data.split(":")[1]
                print(f"  → 텍스트 입력: {text}", flush=True)
                pyautogui.write(text)
                print(f"  ✅ 완료", flush=True)
            else:
                print(f"  ⚠️ 알 수 없는 명령", flush=True)

        except Exception as e:
            print(f"❌ [에러] {addr}: {e}", flush=True)
            break
    
    client_socket.close()
    print(f"🔌 [종료] {addr} 연결 끊김", flush=True)

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"👂 리시버 시작: {HOST}:{PORT}", flush=True)
    sys.stdout.flush()

    try:
        while True:
            client, addr = server.accept()
            print(f"🎯 [수신 준비] {addr}", flush=True)
            sys.stdout.flush()
            
            client_thread = threading.Thread(target=handle_client, args=(client, addr), daemon=True)
            client_thread.start()
    except KeyboardInterrupt:
        print("\n⛔ 서버 종료", flush=True)
    finally:
        server.close()

if __name__ == '__main__':
    start_server()
