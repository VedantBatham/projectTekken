import mediapipe as mp
import cv2
from pynput.keyboard import Controller, Key
import subprocess

# Path to your emulator's executable
emulator_path = r"D:\TEKKEN 7\TekkenGame\Binaries\Win64\TekkenGame-Win64-Shipping_cdx_cracked.exe"
# Launch the emulator
subprocess.Popen(emulator_path, shell=True)

# Initialize MediaPipe Pose, drawing utils, keyboard controller, and webcam
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(model_complexity=1)
keyboard = Controller()
cap = cv2.VideoCapture(0)

# Threshold to determine leaning
lean_threshold = 0.08

# State variables for gestures
is_left_pressed = False
is_right_pressed = False
p_down = False
lp_down = False
llk_down = False
rlk_down = False
jump_down = False
bend_down = False
rage_down = False  # State variable for Rage Art
initial_hip_y = None

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert to RGB (MediaPipe requires RGB input)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)

    if results.pose_landmarks:
        # Extract landmarks for leaning detection
        left_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        left_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
        right_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]

        # Calculate horizontal distances between shoulders and hips
        left_dist = abs(left_shoulder.x - left_hip.x)
        right_dist = abs(right_shoulder.x - right_hip.x)

        # Detect leaning direction
        if left_dist - right_dist > lean_threshold:  # Leaning left
            if not is_left_pressed:  # Key is not already pressed
                print("Leaning Left (Pressing Left Arrow Key)")
                keyboard.press('a')
                is_left_pressed = True
            # Ensure right arrow key is released
            if is_right_pressed:
                print("Releasing Right Arrow Key")
                keyboard.release('d')
                is_right_pressed = False
        elif right_dist - left_dist > lean_threshold:  # Leaning right
            if not is_right_pressed:  # Key is not already pressed
                print("Leaning Right (Pressing Right Arrow Key)")
                keyboard.press('d')
                is_right_pressed = True
            # Ensure left arrow key is released
            if is_left_pressed:
                print("Releasing Left Arrow Key")
                keyboard.release('a')
                is_left_pressed = False
        else:  # Neutral position
            if is_left_pressed:  # Release left arrow key
                print("Releasing Left Arrow Key")
                keyboard.release('a')
                is_left_pressed = False
            if is_right_pressed:  # Release right arrow key
                print("Releasing Right Arrow Key")
                keyboard.release('d')
                is_right_pressed = False

        # Detect right hand punch
        if results.pose_landmarks.landmark[16].visibility > 0.7:
            x = abs(results.pose_landmarks.landmark[16].x * 640 - results.pose_landmarks.landmark[12].x * 640)
            if x > 110:
                print("Right Hand Punch")
                if not p_down:
                    keyboard.press("i")
                    p_down = True
            else:
                if p_down:
                    keyboard.release("i")
                    p_down = False

        # Detect left hand punch
        if results.pose_landmarks.landmark[15].visibility > 0.7:
            x_left = abs(results.pose_landmarks.landmark[15].x * 640 - results.pose_landmarks.landmark[11].x * 640)
            if x_left > 110:
                print("Left Hand Punch")
                if not lp_down:
                    keyboard.press("u")
                    lp_down = True
            else:
                if lp_down:
                    keyboard.release("u")
                    lp_down = False

        # Detect left leg kick
        difference_left_leg = abs((results.pose_landmarks.landmark[25].y*640)- (results.pose_landmarks.landmark[23].y*640))
        if difference_left_leg <= 120:
            print("Left Leg Kick")
            if not llk_down:
                keyboard.press("j")
                llk_down = True
        else:
            if llk_down:
                keyboard.release("j")
                llk_down = False

        # Detect right leg kick
        difference_right_leg = abs((results.pose_landmarks.landmark[26].y*640 )- (results.pose_landmarks.landmark[24].y*640))
        if difference_right_leg <= 120:
            print("Right Leg Kick")
            if not rlk_down:
                keyboard.press("k")
                rlk_down = True
        else:
            if rlk_down:
                keyboard.release("k")
                rlk_down = False
        # Get the y-coordinate of the hip (landmark 24)
        hip_y = results.pose_landmarks.landmark[24].y * 640

        if initial_hip_y is None:
            initial_hip_y = hip_y

        '''# Detect jump based on y-coordinate change
        if hip_y < initial_hip_y - 100:  # Threshold value for detecting a jump
            print("Jump Detected!")
            if not jump_down:
                keyboard.press('w')
                jump_down = True
        else:
            if jump_down:
                keyboard.release('w')
                jump_down = False

        # Detect bend down based on y-coordinate change
        if hip_y > initial_hip_y + 150:  # Threshold value for detecting a bend down
            print("Bend Detected!")
            if not bend_down:
                keyboard.press('s')
                bend_down = True
        else:
            if bend_down:
                keyboard.release('s')
                bend_down = False '''       

        # Detect Rage Art (Both arms raised above head)
        left_hand = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]
        right_hand = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]
        nose = results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE]

        if left_hand.y < nose.y and right_hand.y < nose.y:  # Both hands above head
            print("Rage Art Activated!")
            if not rage_down:
                keyboard.press("o")  # Perform the Rage Art action
                rage_down = True
        else:
            keyboard.release("o")
            rage_down = False  # Reset when hands lower

    # Draw landmarks
    mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # Flip frame for mirror-like display
    frame = cv2.flip(frame, 1)
    cv2.imshow('Gesture Control', frame)

    # Exit on pressing ESC
    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()