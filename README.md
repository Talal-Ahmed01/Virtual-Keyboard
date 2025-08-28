# Virtual-Keyboard
A hand-gesture controlled virtual keyboard built with Python, OpenCV, and MediaPipe — type by pinching your fingers in the air with a translucent overlay on your screen.

# 🖐️ Virtual Keyboard Overlay (Hand Gesture Controlled)

This project implements a **virtual keyboard overlay** that you can interact with using **hand gestures** captured from your webcam. It uses **MediaPipe Hands** for landmark detection, **OpenCV** for rendering the overlay, and **PyAutoGUI** to send keypresses to your system.

The project creates a translucent, click-through window showing a **virtual keyboard**, where you can type by pinching your **thumb** and **index finger** together over a key.

---

## ✨ Features
- 🎥 **Real-time hand tracking** using [MediaPipe Hands](https://developers.google.com/mediapipe/solutions/vision/hand_landmarker).
- ⌨️ **Virtual keyboard overlay** drawn with OpenCV.
- ✋ **Pinch gesture detection** for keypresses.
- 🖱️ **Click-through + always-on-top overlay** (Windows only).
- 🔄 **Smooth pointer movement** with jitter reduction.
- 🔠 Supports **Caps Lock**, **Shift**, and symbols (`! @ # $ % ^ ...`).
- ⌫ **Backspace, Enter, Space** fully functional.
- 🎮 Works with **any application** since keypresses are sent at system level.

---

## 🛠️ Tech Stack
- **Python 3.8+**
- [OpenCV](https://opencv.org/)
- [MediaPipe](https://developers.google.com/mediapipe)
- [PyAutoGUI](https://pyautogui.readthedocs.io/en/latest/)
- [pywin32](https://github.com/mhammond/pywin32) (for Windows overlay control)

---

## 📦 Installation

Clone the repo:
```bash
git clone https://github.com/Talal-Ahmed01/virtual-keyboard-overlay.git
cd virtual-keyboard-overlay
```

▶️ Usage
Run the script:
python virtual_keyboard.py

Controls:
Move your index finger over the virtual keyboard to highlight keys.
Pinch thumb + index finger to "press" a key.
Release pinch to reset.
Press Esc to quit.

⚙️ How It Works
Camera Input
Captures live video from your webcam (1280×720 for stable landmark detection).
Hand Landmark Tracking
MediaPipe Hands detects the 21 hand landmarks.
Pointer & Pinch Detection
Index fingertip acts as a cursor.
Pinch (thumb ↔ index finger) triggers a keypress.
Uses hysteresis + debounce for stable clicking.

Keyboard Overlay
Drawn with OpenCV as a translucent window.
Keys mapped to actual system keypresses via PyAutoGUI.

⚠️ Limitations
Works only on Windows (overlay click-through via pywin32).
Requires a good webcam & lighting for stable detection.
Performance may vary depending on system specs.
