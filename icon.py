import cv2
import mediapipe as mp
import numpy as np
import math
import time
import threading

# Notification library
from plyer import notification

# System tray icon libraries
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw

# Volume control libraries
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# --------------------------- #
# Setup volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
minVol, maxVol = volume.GetVolumeRange()[:2]

# Mediapipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1,
                    min_detection_confidence=0.7,
                    min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Global flag
running = False

# Create Tray Icon
def create_image():
    """Creates a simple tray icon"""
    img = Image.new("RGB", (64, 64), "white")
    d = ImageDraw.Draw(img)
    d.ellipse((16, 16, 48, 48), fill="black")
    return img

# --------------------------- #
# Gesture Control Functions
def start_gesture_control(icon, item):
    global running
    running = True
    threading.Thread(target=gesture_loop, daemon=True).start()
    status_label.config(text="Status: Running", fg="green")

def stop_gesture_control(icon, item):
    global running
    running = False
    status_label.config(text="Status: Stopped", fg="red")

def exit_app(icon, item):
    global running
    running = False
    icon.stop()

minVol, maxVol = volume.GetVolumeRange()[:2]

def gesture_loop():
    cap = cv2.VideoCapture(0)

    while running:
        success, img = cap.read()
        if not success:
            break

        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)

        lmList = []

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                for id, lm in enumerate(handLms.landmark):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy])

                mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

            if len(lmList) >= 9:
                # Thumb tip = 4, Index tip = 8
                x1, y1 = lmList[4][1], lmList[4][2]
                x2, y2 = lmList[8][1], lmList[8][2]

                # Draw circles
                cv2.circle(img, (x1, y1), 10, (255, 0, 0), cv2.FILLED)
                cv2.circle(img, (x2, y2), 10, (255, 0, 0), cv2.FILLED)

                # Draw connecting line
                cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 3)

                # Calculate distance
                length = int(math.hypot(x2 - x1, y2 - y1))

                # Convert distance → volume
                vol = np.interp(length, [20, 200], [minVol, maxVol])
                volume.SetMasterVolumeLevel(vol, None)
                
                # Display Volume Bar
                volBar = np.interp(length, [20, 200], [400, 150])  
                
                # Volume Bar Outline
                cv2.rectangle(img, (50,150), (85,400), (0,255,0), 3)
                # Volume Bar Fill
                cv2.rectangle(img, (50,int(volBar)), (85,400), (0,255,0), cv2.FILLED)

                # Display volume %
                volPer = np.interp(length, [20, 200], [0, 100])
                cv2.putText(img, f"Volume: {int(volPer)}%", (30, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Gesture Volume Control", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        time.sleep(0.01)
        
    cap.release()
    #cv2.destroyAllWindows()

# -- Notification and Startup Setup -- #

notification.notify(
    title="Gesture Volume Control",
    message="Gesture control activated",
    timeout=2
)

# -------------------- RUN TRAY ICON --------------------
def main():
    icon = Icon(
    "Gesture Volume Control",
    create_image(),
    menu=Menu(
                MenuItem("Start Gesture Control", start_gesture_control),
                MenuItem("Stop Gesture Control", stop_gesture_control),
                MenuItem("Exit", exit_app)
            ))

    icon.run()

if __name__ == "__main__":
    main()