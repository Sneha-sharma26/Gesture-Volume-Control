# 🎚️ Gesture Volume Control Using Hand Tracking

A real‑time hand gesture based volume control system using computer vision. This project detects your hand using a webcam and lets you control your system’s volume by the distance between your thumb and index finger — just like a virtual volume knob! 🎧🤚

---

## 🧠 Features

- 📹 Real‑time hand tracking using MediaPipe
- ✋ Volume control via gesture (thumb ↔ index finger)
- 🔊 Visual UI overlay showing current volume level
- ⚡ Lightweight and fast

---

## 🛠️ How It Works

1. **Hand Detection**  
   Uses MediaPipe to detect hand landmarks from webcam video frames.

2. **Distance Calculation**  
   Measures the distance between the thumb tip and the index finger tip.

3. **Volume Mapping**  
   Maps that distance to your system’s volume range.

4. **Smooth Control**  
   When the gesture changes, volume updates live with visual feedback.

---

## 🚀 Technologies Used

| Library | Purpose |
|--------|---------|
| OpenCV | Webcam capture & drawing UI |
| MediaPipe | Hand landmark detection |
| NumPy | Array and math utilities |
| Pycaw | Control Windows system volume |

---

## 📦 Requirements

Make sure you have Python 3.7+ installed.

Install dependencies with:

```bash
pip install -r requirements.txt
```

## 🎯 How to Run

Clone the repository:

```bash
git clone https://github.com/Sneha-sharma26/Gesture-Volume-Control.git
cd Gesture-Volume-Control
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
python main.py
```

👁️ Allow access to your webcam if prompted.

## 🖱️ Controls
| Action | Gesture |
|--------|---------|
| Increase Volume | Move fingers farther apart |
| Decrease Volume | Bring fingers closer together |
| Quit Program | Press q in the window |

## 🧩 Folder Structure

```text
Gesture-Volume-Control/
├── main.py
├── HandTrackingModule.py
├── requirements.txt
└── README.md
```

## 🧪 Expected Output

1. ✔️ Webcam window showing hand
2. ✔️ UI indicating volume level bar
3. ✔️ Real-time volume changing with gestures

## 🏆 Tips for Use

1. Good lighting improves accuracy 🕯️
2. Keep hand within camera range
3. Try with different backgrounds

## 🤝 Contributing

Contributions are welcome! You can:
1. Add support for other OS volume controls
2. Add sound effects
3. Improve visual UI

## 📜 License

Distributed under the **MIT License** — see `LICENSE` for details.