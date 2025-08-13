import cv2

for i in range(6):
    cap = cv2.VideoCapture(i)
    ok = cap.isOpened()
    print(f"Index {i}: opened={ok}")
    if ok:
        ret, frame = cap.read()
        print(f"  read={ret}, shape={None if not ret else frame.shape}")
    cap.release()