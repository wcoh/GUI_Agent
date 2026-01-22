import socket
import pyautogui
import threading
import sys
import time

HOST = '0.0.0.0' 
PORT = 9999

def handle_client(client_socket, addr):
    print(f"🔗 [연결] {addr}", flush=True)
    sys.stdout.flush()
    
    # 연결 확인 응답
    try:
        client_socket.send(b"OK")
    except:
        pass
    
    while True:
        try:
            # 수신 대기
            data = client_socket.recv(1024).decode('utf-8').strip()
            if not data:
                print(f"❌ [종료] {addr} - 데이터 없음", flush=True)
                break
            
            print(f"📨 [수신] {addr}: '{data}'", flush=True)
            sys.stdout.flush()
            
            if data.startswith("MOVE:"):
                try:
                    coords = data.split(":")[1].split(",")
                    x, y = int(coords[0]), int(coords[1])
                    print(f"  → 마우스 이동: ({x}, {y})", flush=True)
                    pyautogui.moveTo(x, y, duration=0.3)
                    print(f"  ✅ 완료", flush=True)
                except Exception as e:
                    print(f"  ❌ 에러: {e}", flush=True)
                
            elif data == "CLICK":
                try:
                    print(f"  → 클릭 실행", flush=True)
                    pyautogui.click()
                    print(f"  ✅ 완료", flush=True)
                except Exception as e:
                    print(f"  ❌ 에러: {e}", flush=True)
                
            elif data.startswith("TYPE:"):
                try:
                    text = data.split(":", 1)[1]
                    print(f"  → 텍스트 입력: {text}", flush=True)
                    pyautogui.write(text)
                    print(f"  ✅ 완료", flush=True)
                except Exception as e:
                    print(f"  ❌ 에러: {e}", flush=True)
            else:
                print(f"  ⚠️ 알 수 없는 명령: '{data}'", flush=True)
            
            sys.stdout.flush()

        except socket.timeout:
            continue
        except Exception as e:
            print(f"❌ [에러] {addr}: {e}", flush=True)
            break
    
    client_socket.close()
    print(f"🔌 [종료] {addr} 연결 끊김", flush=True)

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(10)
    
    print(f"👂 ========================================", flush=True)
    print(f"👂 리시버 시작: {HOST}:{PORT}", flush=True)
    print(f"👂 ========================================", flush=True)
    sys.stdout.flush()

    try:
        while True:
            try:
                client, addr = server.accept()
                client.settimeout(5.0)
                print(f"\n🎯 [새 연결] {addr}", flush=True)
                sys.stdout.flush()
                
                client_thread = threading.Thread(
                    target=handle_client, 
                    args=(client, addr), 
                    daemon=True
                )
                client_thread.start()
            except Exception as e:
                print(f"❌ [수신 에러] {e}", flush=True)
                
    except KeyboardInterrupt:
        print(f"\n⛔ 서버 종료", flush=True)
    finally:
        server.close()

if __name__ == '__main__':
    start_server()
