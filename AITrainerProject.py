import cv2
import numpy as np
import time
import PostModule as pm

# ---------- SETTINGS ----------
CAM_INDEX = 0
FLIP = True
W, H = 1280, 720

# For bicep curl using RIGHT arm:
# shoulder=12, elbow=14, wrist=16 (MediaPipe Pose indices)
P1, P2, P3 = 12, 14, 16

# These depend on your camera angle. You'll calibrate quickly.
ANGLE_DOWN = 160       # arm extended (down)
ANGLE_UP = 45          # arm curled (up)

# ---------- INIT ----------
cap = cv2.VideoCapture(CAM_INDEX)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, W)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, H)

detector = pm.poseDetector()

count = 0
dir = 0  
pTime = 0

while True:
    success, img = cap.read()
    if not success:
        print("Could not read from webcam. Try CAM_INDEX=1.")
        break

    if FLIP:
        img = cv2.flip(img, 1)

    img = cv2.resize(img, (W, H))

    # Pose detection
    img = detector.findPose(img, draw=True)
    lmList = detector.findPosition(img, draw=False)

    if len(lmList) != 0:
        # Angle (draw points/lines inside findAngle if you want)
        angle = detector.findAngle(img, P1, P2, P3, draw=True)

        # Map angle -> percent (0..100)
        per = np.interp(angle, (ANGLE_UP, ANGLE_DOWN), (100, 0))
        bar = np.interp(angle, (ANGLE_UP, ANGLE_DOWN), (100, 650))

        # Rep counting logic
        if per == 100:
            if dir == 0:
                count += 0.5
                dir = 1
        if per == 0:
            if dir == 1:
                count += 0.5
                dir = 0

        # ----- UI (bar + text) -----
        # Bar outline
        cv2.rectangle(img, (1150, 100), (1210, 650), (255, 255, 255), 3)
        # Bar fill
        cv2.rectangle(img, (1150, int(bar)), (1210, 650), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, f"{int(per)}%", (1120, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Count box
        cv2.rectangle(img, (20, 520), (250, 700), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, str(int(count)), (70, 660),
                    cv2.FONT_HERSHEY_SIMPLEX, 4, (255, 0, 0), 6)

    # FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime) if (cTime - pTime) > 0 else 0
    pTime = cTime
    cv2.putText(img, f"FPS: {int(fps)}", (20, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow("AI Trainer (Webcam)", img)

    # Press q to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
