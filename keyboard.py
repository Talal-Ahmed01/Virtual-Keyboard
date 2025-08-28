import cv2
import mediapipe as mp
import pyautogui
import time
import math
import win32gui
import win32con
from collections import deque
import numpy as np

# Overlay window (topmost + click-through)

WS_EX_LAYERED      = 0x00080000
WS_EX_TRANSPARENT  = 0x00000020
SWP_FLAGS_TOPMOST  = win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE

def apply_clickthrough_topmost(window_name):
    hwnd = win32gui.FindWindow(None, window_name)
    if hwnd:
        styles = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        styles |= (WS_EX_LAYERED | WS_EX_TRANSPARENT)
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, styles)
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, SWP_FLAGS_TOPMOST)


# Camera & overlay window
CAM_W, CAM_H = 1280, 720
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_W)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_H)

WIN_W, WIN_H = 1200, 600
WINDOW_NAME = "Virtual Keyboard Overlay"
cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
cv2.resizeWindow(WINDOW_NAME, WIN_W, WIN_H)
cv2.moveWindow(WINDOW_NAME, 100, 100)

clickthrough_set = False
last_style_check = 0

# MediaPipe Hands

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
    max_num_hands=2
)
mp_draw = mp.solutions.drawing_utils

# Keyboard layout
keys_rows = [
    ["1","2","3","4","5","6","7","8","9","0","-","=","Backspace"],
    ["Q","W","E","R","T","Y","U","I","O","P","[","]","\\"],
    ["Caps","A","S","D","F","G","H","J","K","L",";","'","Enter"],
    ["Shift","Z","X","C","V","B","N","M",",",".","/","Shift"],
    ["Space"]
]
KEY_W, KEY_H, KEY_GAP = 60, 60, 8

# Pinch detection (thumb ↔ fingertip) with hysteresis + debounce
# Use thresholds relative to hand size so it works at any distance.
PINCH_DOWN_RATIO = 0.22  
PINCH_UP_RATIO   = 0.32
DEBOUNCE_MS      = 120

FINGERTIPS = {"index": 8, "middle": 12, "ring": 16, "pinky": 20}
THUMB_TIP = 4
pinching = {}        
last_click_ms = {}   

# smoothing to reduce jitter
smooth_pts = {} 
def smooth(key, x, y, n=5):
    dq = smooth_pts.setdefault(key, deque(maxlen=n))
    dq.append((x, y))
    sx = sum(p[0] for p in dq) / len(dq)
    sy = sum(p[1] for p in dq) / len(dq)
    return int(sx), int(sy)

# Modifiers
caps = False
active_shift = False

shift_map = {
    '1':'!', '2':'@','3':'#','4':'$','5':'%',
    '6':'^','7':'&','8':'*','9':'(','0':')',
    '-':'_','=':'+','[':'{',']':'}','\\':'|',
    ';':':',"'":'"',',':'<','.':'>','/':'?'
}

def render_keyboard(canvas):
    """Draw a translucent keyboard on canvas and return {key: (x,y,w,h)}."""
    start_y = 250
    key_positions = {}

    overlay = canvas.copy()
    for r, row in enumerate(keys_rows):
        x = 50
        y = start_y + r * (KEY_H + KEY_GAP)
        for key in row:
            w = KEY_W * 2 if key in ["Backspace","Enter","Caps","Shift"] else (KEY_W * 6 if key=="Space" else KEY_W)
            cv2.rectangle(overlay, (x, y), (x + w, y + KEY_H), (203, 192, 255), -1)
            tx = x + 10 if key != "Space" else x + w // 4
            ty = y + 38
            cv2.putText(canvas, key, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
            key_positions[key] = (x, y, w, KEY_H)
            x += w + KEY_GAP
    cv2.addWeighted(overlay, 0.35, canvas, 0.65, 0, canvas)
    return key_positions

def key_at(px, py, key_positions):
    for k, (x, y, w, h) in key_positions.items():
        if x <= px <= x+w and y <= py <= y+h:
            return k
    return None

def type_key(k):
    global caps, active_shift
    if k == "Backspace": pyautogui.press("backspace"); return
    if k == "Enter":     pyautogui.press("enter");     return
    if k == "Space":     pyautogui.press("space");     return
    if k == "Caps":      caps = not caps;              return
    if k == "Shift":     active_shift = True;          return

    ch = k
    if ch.isalpha():
        ch = ch.upper() if (caps ^ active_shift) else ch.lower()
    elif active_shift:
        ch = shift_map.get(ch, ch)

    pyautogui.typewrite(ch)
    if active_shift:
        active_shift = False  # one-shot clears after a non-modifier

def norm_distance(ax, ay, bx, by):
    return math.hypot(ax - bx, ay - by)

def hand_size_norm(lm):
    """Approx hand size using wrist↔middle MCP distance (normalized)."""
    # wrist (0) and middle_mcp (9) in normalized coords
    wx, wy = lm[0].x, lm[0].y
    mx, my = lm[9].x, lm[9].y
    return math.hypot(mx - wx, my - wy) + 1e-6  # avoid zero

# Main loop
while True:
    ok, cam_frame = cap.read()
    if not ok:
        break

    # Process landmarks on native camera frame
    cam_frame = cv2.flip(cam_frame, 1)
    cam_h, cam_w = cam_frame.shape[:2]
    results = hands.process(cv2.cvtColor(cam_frame, cv2.COLOR_BGR2RGB))

    # Prepare overlay canvas
    # Black background instead of camera feed
    canvas = np.zeros((WIN_H, WIN_W, 3), dtype=np.uint8)    #--This if you want no cam
    #canvas = cv2.resize(cam_frame, (WIN_W, WIN_H))
    key_positions = render_keyboard(canvas)

    # Draw + interact
    if results.multi_hand_landmarks:
        for h_idx, hand in enumerate(results.multi_hand_landmarks):
            lm = hand.landmark

            # compute hand scale
            hs = hand_size_norm(lm)
            pinch_down = PINCH_DOWN_RATIO * hs
            pinch_up   = PINCH_UP_RATIO   * hs

            # Thumb tip
            tx_n, ty_n = lm[THUMB_TIP].x, lm[THUMB_TIP].y

            # Index fingertip
            fx_n, fy_n = lm[FINGERTIPS["index"]].x, lm[FINGERTIPS["index"]].y

            # distance in normalized space
            dist_n = norm_distance(fx_n, fy_n, tx_n, ty_n)

            # scale fingertip to overlay coords (use index finger for pointer)
            fx = int(fx_n * WIN_W)
            fy = int(fy_n * WIN_H)
            fx, fy = smooth((h_idx, "index"), fx, fy)

            # draw fingertip (pointer)
            cv2.circle(canvas, (fx, fy), 8, (0, 255, 0), cv2.FILLED)

            key_id = (h_idx, "index")
            if key_id not in pinching:
                pinching[key_id] = False
                last_click_ms[key_id] = 0.0

            # Edge: pinch down (thumb + index together)
            if not pinching[key_id] and dist_n < pinch_down:
                pinching[key_id] = True
                now = time.time() * 1000.0
                if now - last_click_ms[key_id] > DEBOUNCE_MS:
                    last_click_ms[key_id] = now
                    hit = key_at(fx, fy, key_positions)
                    if hit:
                        x, y, w, h = key_positions[hit]
                        cv2.rectangle(canvas, (x, y), (x+w, y+h), (0, 200, 0), 3)
                        type_key(hit)

            elif pinching[key_id] and dist_n > pinch_up:
                pinching[key_id] = False

    #show & maintain window flags
    cv2.imshow(WINDOW_NAME, canvas)
    if not clickthrough_set:
        cv2.waitKey(1)  # ensure window exists
        apply_clickthrough_topmost(WINDOW_NAME)
        clickthrough_set = True
        last_style_check = time.time()

    if time.time() - last_style_check > 3.0:
        apply_clickthrough_topmost(WINDOW_NAME)
        last_style_check = time.time()

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()