# 🖐️ Virtual-Keyboard & Mouse (Hand-Gesture Controlled)

A pair of Python tools that let you **type and control the cursor using hand gestures** captured from your webcam.  
- **keyboard.py** → On-screen translucent **virtual keyboard** you can press by **pinching** your thumb and index finger.  
- **mouse.py** → **Mouse control** mapped to your index fingertip; **click** by bringing index and middle fingertips together.

Built with **OpenCV**, **MediaPipe**, **PyAutoGUI**, and (for Windows overlay) **pywin32**.

---
## ✨ Features
### Keyboard (keyboard.py)
- 🎥 Real-time hand tracking (MediaPipe Hands).
- ⌨️ Translucent, click-through **virtual keyboard overlay** (Windows).
- 🤏 **Pinch to type** (thumb ↔ index).
- 🔠 **Caps**, **Shift** (one-shot), symbols (`!@#$%^&*()_+{}|:"<>?`), ⌫ **Backspace**, **Enter**, **Space**.
- 🔄 Jitter smoothing + **debounce/hysteresis** to avoid accidental keypresses.
- 🖼️ Can run with **black background** (no camera feed on screen).

### Mouse (mouse.py)
- 🖱️ Cursor follows **index fingertip** (camera coords → screen coords).
- 👆 **Click** by tapping **index** and **middle** fingertips together (distance threshold + cooldown).
- ⚡ Simple, responsive, and app-agnostic (system-level events).

---
## 🛠️ Tech Stack
- **Python 3.8+**
- [OpenCV](https://opencv.org/)
- [MediaPipe](https://developers.google.com/mediapipe)
- [PyAutoGUI](https://pyautogui.readthedocs.io/en/latest/)
- [pywin32](https://github.com/mhammond/pywin32) *(keyboard overlay click-through on Windows)*

---
## 📦 Installation

Clone the repo:
```bash
git clone https://github.com/Talal-Ahmed01/virtual-keyboard-overlay.git
cd virtual-keyboard-overlay
````

Install dependencies:
```bash
pip install opencv-python mediapipe pyautogui pywin32
```

> Tip: If you only need the **mouse** tool on macOS/Linux, you can skip `pywin32`.
---

## ▶️ Usage
### 1) Virtual Keyboard

Run:

```bash
python keyboard.py
```

Controls:

* Move **index finger** over a key.
* **Pinch** (thumb ↔ index) to **press** the key.
* **Caps** toggles case; **Shift** is one-shot (applies to next key).
* **Esc** to quit.

**Want a black background (no camera preview)?**
Add:

```python
import numpy as np
canvas = np.zeros((WIN_H, WIN_W, 3), dtype=np.uint8)
```

in place of where the camera frame is copied to `canvas`.
(You can also comment out the fingertip `cv2.circle` to hide the pointer.)

---

### 2) Gesture Mouse

Save your script as `mouse.py` and run:

```bash
python mouse.py
```

Behavior:

* Cursor position = index fingertip.
* **Click** when **index** and **middle** fingertips come within the `click_threshold`.
* Adjustable:

  * `click_threshold` (pixels, camera space)
  * `click_cooldown` (seconds)
* **Esc** to quit.

---

## ⚙️ How It Works

**MediaPipe Hands** detects 21 landmarks per hand.

* **Keyboard**: We scale and smooth the **index fingertip** position to overlay coordinates and use **pinch distance** (thumb ↔ index) with **hysteresis** to trigger a key. Keys are rendered with OpenCV and typed with PyAutoGUI.
* **Mouse**: We map camera coordinates of the index fingertip to **screen coordinates** and send `moveTo`. A **click** occurs when the **index–middle** fingertip distance drops below a threshold (with cooldown to prevent spam).

---
## ⚠️ Limitations

* The **keyboard overlay** window’s click-through + always-on-top is **Windows-only** (uses `pywin32`).
* Proper lighting and a decent webcam help landmark stability.
* Performance depends on system specs and camera resolution.

---
## 🔧 Troubleshooting

* **No camera**: Ensure another app isn’t using the webcam.
* **Laggy/unstable**: Reduce camera resolution or increase gesture thresholds.
* **Wrong screen mapping** (mouse): Verify `cam_width/cam_height` align with your `VideoCapture` settings.

---
## 🚀 Roadmap Ideas

* Cross-platform overlay click-through.
* Multi-finger gestures (scroll, right-click, hotkeys).
* Themeable keyboard + resizable layout.
* Word suggestions / predictive typing.

---
## 🙌 Acknowledgements

* [MediaPipe](https://developers.google.com/mediapipe)
* [OpenCV](https://opencv.org/)
* [PyAutoGUI](https://pyautogui.readthedocs.io/en/latest/)

### 👤 Author
**Talal-Ahmed01**
