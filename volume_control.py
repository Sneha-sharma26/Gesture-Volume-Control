from flask import Flask, render_template, jsonify, Response
import threading

import cv2 
import mediapipe as mp
import math
import numpy as np

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# -------------------- Flask App -------------------- #
app = Flask(__name__)

# Initialize webcam
cap = cv2.VideoCapture(0)
mpHands = mp.solutions.hands       # mp = mediapipe
hands = mpHands.Hands(max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7)     # Hand detection Object
mpDraw = mp.solutions.drawing_utils

# Initialize pycaw for volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

minVol, maxVol = volume.GetVolumeRange()[:2]

# -------------------- Global State -------------------- #
gesture_running = False
current_volume_percent = 0

# -------- SMOOTHING VARIABLES -------- #
volume_history = []
SMOOTHING_WINDOW = 5   # number of frames to average


def gen_frames():
    global gesture_running, current_volume_percent, volume_history
    
    while gesture_running:
        success, img = cap.read()
        if not success:
            print("Failed to capture video")
            break
    
        # OpenCV uses BGR format by default but mediapipe requires RGB
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)  # sends RGB image to hands detection model
    
        if results.multi_hand_landmarks:  # multi_hand_landmarks = list of all hands detected
            for handLms in results.multi_hand_landmarks:
                # handLms = landmarks of one hand
                lmList = []
                for id, lm in enumerate(handLms.landmark):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy])

                mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

            # Thumb tip = id 4
            # Index tip = id 8
            x1, y1 = lmList[4][1], lmList[4][2]
            x2, y2 = lmList[8][1], lmList[8][2]

            cv2.circle(img, (x1, y1), 10, (255, 0, 0), cv2.FILLED)
            cv2.circle(img, (x2, y2), 10, (255, 0, 0), cv2.FILLED)

            # Line between thumb and index finger tips
            cv2.line(img, (x1,y1), (x2,y2), (0,255,0), 3)

            # Distance between thumb and index finger tips
            length = int(math.hypot(x2-x1, y2-y1))

            cv2.putText(img, f"Distance: {length}", (30,100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,255), 2)

            # ---------------- VOLUME CONTROL SECTION ---------------- #
        
            # Map distance (20 to 200) → volume range (minVol to maxVol)
            vol = np.interp(length, [20, 200], [minVol, maxVol])

            # Simple Moving Average Smoothing
            volume_history.append(vol)
            if len(volume_history) > SMOOTHING_WINDOW:
                volume_history.pop(0)

            smooth_volume = sum(volume_history) / len(volume_history)

            # Set smoothed volume
            volume.SetMasterVolumeLevel(smooth_volume, None)
            
            # Display Volume % and Volume Bar
            volBar = np.interp(length, [20, 200], [400, 150])  # Bar height
            volPer = np.interp(length, [20, 200], [0, 100])    # Percentage

            current_volume_percent = int(volPer)
            
            # Volume Bar Outline
            cv2.rectangle(img, (50,150), (85,400), (0,255,0), 3)
            # Volume Bar Fill
            cv2.rectangle(img, (50,int(volBar)), (85,400), (0,255,0), cv2.FILLED)

            # Volume Percentage Text
            cv2.putText(img, f"{int(volPer)} %", (40, 430),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        _, buffer = cv2.imencode('.jpg', img)
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

# ---------------------------------- #
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/start", methods=["POST"])
def start_gesture():
    """Start gesture control"""
    global gesture_running
    if not gesture_running:
        gesture_running = True
    return jsonify({"status": "started"})

@app.route("/stop", methods=["POST"])
def stop_gesture():
    """Stop gesture control"""
    global gesture_running
    gesture_running = False
    return jsonify({"status": "stopped"})

@app.route("/volume")
def get_volume():
    """Send current volume % to UI"""
    return jsonify({"volume": current_volume_percent})

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)