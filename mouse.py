import cv2
import mediapipe as mp
import pyautogui
import time
import math

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

screen_width, screen_height = pyautogui.size()
cam_width, cam_height = 740, 580

click_threshold = 30   # distance between index and middle finger for click
click_cooldown = 0.3
last_click_time = 0


# Camera setup
cap = cv2.VideoCapture(0)
cap.set(3, cam_width)
cap.set(4, cam_height)

# Main loop
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, handLms, mp_hands.HAND_CONNECTIONS)
            lmList = handLms.landmark

            # Get coordinates of index finger tip
            x_index = int(lmList[8].x * cam_width)
            y_index = int(lmList[8].y * cam_height)

            # Map camera coordinates to screen coordinates
            screen_x = int(x_index * screen_width / cam_width)
            screen_y = int(y_index * screen_height / cam_height)

            # Move mouse
            pyautogui.moveTo(screen_x, screen_y)

            # Detect click: distance between index tip and middle tip
            x_middle = int(lmList[12].x * cam_width)
            y_middle = int(lmList[12].y * cam_height)
            distance = math.hypot(x_index - x_middle, y_index - y_middle)
            current_time = time.time()

            if distance < click_threshold and current_time - last_click_time > click_cooldown:
                last_click_time = current_time
                pyautogui.click()  # left click

    cv2.imshow("Mouse Control", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC to exit
        break

cap.release()
cv2.destroyAllWindows()