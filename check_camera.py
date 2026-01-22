import cv2

# HDMI 캡처보드 인식 확인
for i in range(10):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print(f"✅ 카메라 인덱스 {i}: 작동 중 - {frame.shape}")
        else:
            print(f"❌ 카메라 인덱스 {i}: 열려있지만 프레임 못 읽음")
        cap.release()
    else:
        print(f"❌ 카메라 인덱스 {i}: 감지 안 됨")
