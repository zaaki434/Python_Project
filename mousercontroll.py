import cv2
import pyautogui
import mediapipe as mp
import time

cap = cv2.VideoCapture(0)
screen_width, screen_height = pyautogui.size()

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2,
                       min_detection_confidence=0.5, min_tracking_confidence=0.5)

mp_drawing = mp.solutions.drawing_utils

# Variables for drag functionality
drag_start_time = None
is_dragging = False
drag_threshold = 0.5  # seconds

def is_high_five(hand_landmarks):
    return all([
        hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y < 
        hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP].y,
        hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y < 
        hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y,
        hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y < 
        hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_PIP].y,
        hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].y < 
        hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_PIP].y
    ])

def is_grab(hand_landmarks):
    return all([
        hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y > 
        hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP].y,
        hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y > 
        hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP].y,
        hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y > 
        hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_PIP].y,
        hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].y > 
        hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_PIP].y
    ])

while True:
    ret, frame = cap.read()
    if not ret:
        break

    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(image_rgb)

    if result.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(result.multi_hand_landmarks, result.multi_handedness):
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            if handedness.classification[0].label == 'Right':
                # Right hand controls pointer
                if is_high_five(hand_landmarks):
                    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    cursor_x = int(index_tip.x * screen_width)
                    cursor_y = int(index_tip.y * screen_height)
                    pyautogui.moveTo(cursor_x, cursor_y)
            
            elif handedness.classification[0].label == 'Left':
                # Left hand controls clicking and dragging
                if is_grab(hand_landmarks):
                    if drag_start_time is None:
                        drag_start_time = time.time()
                    elif time.time() - drag_start_time > drag_threshold:
                        if not is_dragging:
                            pyautogui.mouseDown()
                            is_dragging = True
                else:
                    if drag_start_time is not None and time.time() - drag_start_time <= drag_threshold:
                        pyautogui.click()  # Short grab results in a click
                    if is_dragging:
                        pyautogui.mouseUp()
                        is_dragging = False
                    drag_start_time = None

    else:
        if is_dragging:
            pyautogui.mouseUp()
            is_dragging = False
        drag_start_time = None

    cv2.imshow('Hand Gesture', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
