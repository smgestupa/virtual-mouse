# %% [markdown]
# ### Import Libraries

# %%
# %pip install opencv-python
# %pip install mediapipe
# %pip install pyautogui
# %pip install tensorflow
# %pip install tkinter

# %%
import csv
import copy
import cv2
import numpy as np
import mediapipe as mp
import HandTracking as tracking
import ProgramStatus as status
import pyautogui
import time
import copy
from sign_language import calc_landmark_list, pre_process_landmark
from models import KeyPointClassifier

# %% [markdown]
# ### Initialize Capturing Variables

# %%
# Capture first webcam
cap = cv2.VideoCapture(0)
 
# Declare capturing frame's width & height
wCam, hCam = 640, 360

cap.set(cv2.CAP_PROP_FRAME_WIDTH, wCam)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, hCam)

# Declare capturing frame's width and height bounding box
bbox_x = 200
bbox_y = 100

# %% [markdown]
# ### Initialize Hand Detector Module

# %%
# Initialize Hand Tracking module
hand_tracking = tracking.HandTracking(maxHands=2, detectionCon=0.7, trackCon=0.7) # Detect only one hand

# Remove pyautogui pause
pyautogui.PAUSE = 0

# Disable pyautogui fail safe
pyautogui.FAILSAFE = False

# Identify screen size
wScreen, hScreen = pyautogui.size()

# %% [markdown]
# ## Initialize Sign Language Module

# %%
# Initialize keypoint classifier
keypoint_classifier = KeyPointClassifier()

# Declare labels for keypoints
with open('models\keypoint_classifier\keypoint_classifier_label.csv', encoding='utf-8-sig') as file:
    keypoint_classifier_labels = csv.reader(file)
    keypoint_classifier_labels = [row[0] for row in keypoint_classifier_labels]

# %% [markdown]
# #### Declare Sign Language Recognition

# %%
def recognizeSignLanguage(frame, hand):
    landmark_list = calc_landmark_list(frame, hand)
    preprocessed_landmark_list = pre_process_landmark(landmark_list)

    hand_sign_id = keypoint_classifier(preprocessed_landmark_list)

    return keypoint_classifier_labels[hand_sign_id]

# %% [markdown]
# ## Initialize Program Status Module

# %%
# Initialize Program Status Module
program_status = status.ProgramStatus()

# Initialize Tkinter window
status_window = program_status.initialize_window()

# Set options for status window
status_window.resizable(False, False) # Disable resizing for width and height
status_window.attributes('-topmost', True) # Window will always be on top
status_window.overrideredirect(True) # Remove window title bar
status_window.geometry(('+%d+%d' % (wScreen - 340, hScreen - 130))) # Position window to this specific x and y coordinates in the screen

# %% [markdown]
# ## Initialize Smoothening Variables

# %%
# Declare the value for smoothening
smoothening = 10 # For cursor moving
drag_smoothening = 60 # For cursor dragging

# Declare the variables of getting previous x and y coordinates
prev_x, prev_y = 0, 0

# Declare the variables of getting current x and y coordinates
curr_x, curr_y = 0, 0

# %% [markdown]
# ## Capture Frames

# %% [markdown]
# ### Preprocess Frame

# %%
def preprocessFrame(frame):
    preprocessed_frame = copy.deepcopy(frame)
    preprocessed_frame = cv2.cvtColor(preprocessed_frame, cv2.COLOR_BGR2RGB)
    
    hsv = cv2.cvtColor(preprocessed_frame, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    lim = 255 - 30
    v[v > lim] = 255
    v[v <= lim] += 30

    final_hsv = cv2.merge((h, s, v))
    preprocessed_frame = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)

    return preprocessed_frame

# %% [markdown]
# #### Declare Virtual Mouse

# %%
def moveMouse(frame, last_action, first_index_x, first_index_y):
    # Define global variables
    global curr_x, curr_y, prev_x, prev_y

    # Declare the initial virtual mouse's x and y coordinates 
    pointer_x = 0
    pointer_y = 0

    # Declare pointers x and y coordinates
    pointer_x = np.interp(first_index_x, (280, (wCam + bbox_x) - 340), (0, wScreen))
    pointer_y = np.interp(first_index_y, (50, (hCam - 50) - bbox_y), (0, hScreen))

    # Check if the last action is drag
    if last_action == 'drag':
        # Define the current x and y coordinates with smoothening for dragging
        curr_x = prev_x + (pointer_x - prev_x) / drag_smoothening
        curr_y = prev_y + (pointer_y - prev_y) / drag_smoothening
    
    # If the last action is anything but the drag
    else:
        # Define the current x and y coordinates with normal smoothening
        curr_x = prev_x + (pointer_x - prev_x) / smoothening
        curr_y = prev_y + (pointer_y - prev_y) / smoothening

    # Move mouse with pyautogui
    pyautogui.moveTo(curr_x, curr_y)

    # Draw a circle to index finger
    cv2.circle(img=frame, center=(first_index_x, first_index_y), radius=10, color=(255, 255, 255))

    # Define the current x and y coordinates as previous
    prev_x = curr_x
    prev_y = curr_y

# %% [markdown]
# ### Start the Program

# %%
# Declare variable to store the last action
last_action = None

# Declare variable the status of input mode
input_mode = False

# Declare the initial input's wait time
input_wait_time = 0 

# Declare the initial input's interval time
input_interval_time = 0

# Declare the initial input's sign alphabet
input_hand_sign = ''

while True:
    # Read current frame
    retrieved, frame = cap.read()

    # Check if no frame is detected
    if not retrieved or program_status.destroy:
        break # Stop the program

    # Modify current frame
    frame = cv2.flip(frame, 1) # Flip frame

    # Duplicate the current frame and preprocess it
    preprocessed_frame = preprocessFrame(frame)

    # Find one or more hands in a preprocessed frame
    results = hand_tracking.findHands(preprocessed_frame)

    # Get the label of hands currently detected by the system
    handedness = results.multi_handedness
    # Assume no hands are detected
    hands_detected = 0

    # Declare variable to store the first hand detected
    first_hand = None

    # Get the current milliseconds
    current_milliseconds = round(time.time() * 1000)

    if handedness != None:
        # Get the number of hands detected
        hands_detected = len(handedness)

        # Get the first label from handedness to set as the first hand
        first_hand = handedness[0].classification[0].label

    # Check if two hands are detected 
    if hands_detected == 2:
        # Get the second label from handedness to set as the first hand
        first_hand = handedness[1].classification[0].label

    # First check if the input mode is on,
    # the last action is to read the input,
    # and there are less than 2 hands detected
    if input_mode and last_action == 'read_input' and hands_detected < 2:
        # Check if less than 2 hands are detected
        if input_wait_time == 0:
            # Set the input's wait time to current milliseconds
            input_wait_time = round(time.time() * 1000)

        # Check if equal or more than 3 seconds have passed
        if (current_milliseconds - input_wait_time) >= 3000:
            # Turn off input mode
            input_mode = False
            # Clear the last action variable
            last_action = None
            # Set the input's wait time back to zero
            input_wait_time = 0
            # Set the input's interval time back to zero
            input_interval_time = 0

            program_status.change_status('Moving Cursor')
            input_hand_sign = ''

    # Check again the same conditions as above,
    # since these conditions will change if more
    # than 3 seconds have passed,
    # however we'll also check if two hands are detected
    elif input_mode and last_action == 'read_input' and hands_detected == 2:
        input_wait_time = 0

        first_lmList, first_hand = None, None
        second_lmList, _ = None, None

        if handedness[1].classification[0].label == 'Right':
            # Get the landmark lists of the first hand detected from index 1
            first_lmList, first_hand = hand_tracking.findPosition(frame, handNo=1)
            # Get the landmark list of the first hand detected from index 0
            second_lmList, _ = hand_tracking.findPosition(frame, handNo=0)

        else:
            # Get the landmark lists of the first hand detected from index 1
            first_lmList, first_hand = hand_tracking.findPosition(frame, handNo=0)
            # Get the landmark list of the first hand detected from index 0
            second_lmList, _ = hand_tracking.findPosition(frame, handNo=1)
            
        # Get the fingers up for the first hand
        first_fingers = hand_tracking.fingersUp(first_lmList)
        # Declare variable to store the fingers up of the second hand detected
        second_fingers = hand_tracking.fingersUp(second_lmList)

        hand_sign = recognizeSignLanguage(preprocessed_frame, first_hand)

        if input_hand_sign != hand_sign:
            input_hand_sign = hand_sign

            if second_fingers[0] == 1 and second_fingers[1:].count(0) == 4:
                program_status.change_status(f'Detected Sign: _')

            else:
                program_status.change_status(f'Detected Sign: {input_hand_sign}')

            input_interval_time = current_milliseconds
        
        elif second_fingers[0] == 1 and second_fingers[1:].count(0) == 4 and (current_milliseconds - input_interval_time) >= 1000:
            pyautogui.write(' ')
            input_interval_time = 0
            input_hand_sign = ''

        elif second_fingers.count(1) == 5 and (current_milliseconds - input_interval_time) >= 1000:
            pyautogui.write(input_hand_sign)
            input_interval_time = 0
            input_hand_sign = ''

    # Check if input mode is on
    # and the first hand detected is a right hand
    elif input_mode and first_hand == 'Right':
        # Get the landmark list of the first hand detected from index 0
        first_lmList, _ = hand_tracking.findPosition(preprocessed_frame)

        # Get the fingers up for the first hand
        first_fingers = hand_tracking.fingersUp(first_lmList)

        # Check if only one hand is detected
        if hands_detected == 1:
            # Get the landmark list of the first hand detected from index 0
            first_lmList, _ = hand_tracking.findPosition(preprocessed_frame)

            # Get the fingers up for the first hand
            first_fingers = hand_tracking.fingersUp(first_lmList)

        # If more than one hand is detected
        else:
            # Get the landmark list of the first hand detected from index 1
            first_lmList, _ = hand_tracking.findPosition(preprocessed_frame, handNo=1)
            # Get the landmark list of the first hand detected from index 0
            second_lmList, _ = hand_tracking.findPosition(preprocessed_frame, handNo=0)

            # Get the fingers up for the first hand
            first_fingers = hand_tracking.fingersUp(first_lmList)
            # Declare variable to store the fingers up of the second hand detected
            second_fingers = hand_tracking.fingersUp(second_lmList)

        # # Get the tips of our fingers for the first hand
        first_thumb_x, first_thumb_y = first_lmList[4][1:] # Thumb finger
        first_index_x, first_index_y = first_lmList[8][1:] # Index finger

        # Get the distance between thumb and index fingers for the first hand
        first_index_l, _ = hand_tracking.findDistance(first_lmList, 4, 8)

        # Get the distance between thumb and ring fingers for the first hand
        first_ring_l, _ = hand_tracking.findDistance(first_lmList, 4, 16)

        # Check if last action was a click
        if last_action == 'wait_input_l_click' and first_index_l > 30:
            cv2.circle(img=frame, center=(first_thumb_x, first_thumb_y), radius=10, color=(255, 255, 255))
            cv2.circle(img=frame, center=(first_index_x, first_index_y), radius=10, color=(255, 255, 255))

            pyautogui.click(interval=0.05) # Do a left click
            last_action = 'read_input'
            program_status.change_status('Detecting Sign Gestures')

        elif last_action == 'leave_input' and first_ring_l > 15:
            last_action = None
            input_mode = False

        elif first_index_l <= 15:
            last_action = 'wait_input_l_click'

        elif first_ring_l <= 15:
            last_action = 'leave_input'

        # Move virtual mouse
        if last_action == 'wait_input':
            moveMouse(frame, last_action, first_index_x, first_index_y)

    # Check if the first hand detected is a right hand
    elif not input_mode and first_hand == 'Right':
        # Draw the capturing frame's bounding box for the right hand
        cv2.rectangle(frame, (280, 50), ((wCam + bbox_x) - 340, (hCam - 50) - bbox_y), (255, 255, 255), 2)

        first_lmList, first_landmark_list = None, None

        # Check if only one hand is detected
        if hands_detected == 1:
            # Get the landmark list of the first hand detected from index 0
            first_lmList, first_landmark_list = hand_tracking.findPosition(preprocessed_frame, handNo=0)

        # If more than one hand is detected
        else: 
            # Get the landmark list of the first hand detected from index 1
            first_lmList, first_landmark_list = hand_tracking.findPosition(preprocessed_frame, handNo=1)

        # Get the fingers up for the first hand
        first_fingers = hand_tracking.fingersUp(first_lmList)

        # Get the tips of our fingers for the first hand
        first_thumb_x, first_thumb_y = first_lmList[4][1:] # Thumb finger
        first_index_x, first_index_y = first_lmList[8][1:] # Index finger
        first_middle_x, first_middle_y = first_lmList[12][1:] # Middle finger

        # Get the distance between thumb and index fingers for the first hand
        first_index_l, _ = hand_tracking.findDistance(first_lmList, 4, 8)

        # Get the distance between thumb and middle fingers for the first hand
        first_middle_l, _ = hand_tracking.findDistance(first_lmList, 4, 12)

        # Get the distance between index and middle fingers for the first hand
        first_tower_l, _ = hand_tracking.findDistance(first_lmList, 8, 12)

        # Get the distance between thumb and ring fingers for the first hand
        first_ring_l, _ = hand_tracking.findDistance(first_lmList, 4, 16)

        if last_action == 'l_click' and first_fingers.count(1) == 2 and first_tower_l <= 15:
            last_action = 'drag'

        elif last_action == 'drag' and first_fingers.count(1) != 2  and first_tower_l > 15:
            pyautogui.mouseUp(duration=0.05, button='left')

            last_action = None

        # Check if currently dragging
        elif last_action == 'drag' and first_fingers.count(1) == 2 and first_tower_l <= 15:
            cv2.circle(img=frame, center=(first_index_x, first_index_y), radius=10, color=(255, 255, 255))
            cv2.circle(img=frame, center=(first_middle_x, first_middle_y), radius=10, color=(255, 255, 255))

            pyautogui.mouseDown(button='left') # Hold the mouse down for dragging
            program_status.change_status('Dragging Cursor')

        # Check if last action was a click
        elif last_action == 'l_click' and first_index_l > 15:
            cv2.circle(img=frame, center=(first_thumb_x, first_thumb_y), radius=10, color=(255, 255, 255))
            cv2.circle(img=frame, center=(first_index_x, first_index_y), radius=10, color=(255, 255, 255))

            program_status.change_status('Left Click Detected')

            pyautogui.click(interval=0.05) # Do a left click
            last_action = None

        # Check if thumb and middle fingers are close to each other
        elif last_action == 'r_click' and first_middle_l > 15:
            cv2.circle(img=frame, center=(first_thumb_x, first_thumb_y), radius=10, color=(255, 255, 255))
            cv2.circle(img=frame, center=(first_middle_x, first_middle_y), radius=10, color=(255, 255, 255))
            
            program_status.change_status('Right Click Detected')

            pyautogui.click(button='right', interval=0.25) # Do a right click
            last_action = None

        # Check if last action is to start input mode 
        # and the thumb and ring fingers are close to each other
        elif last_action == 'start_input' and first_ring_l > 15:
            last_action = 'wait_input'
            input_mode = True
            program_status.change_status('Click on a Text Field')

        elif (first_tower_l <= 15 and first_fingers.count(1) == 2) or first_index_l <= 15:
            last_action = 'l_click'

        elif first_middle_l <= 15:
            last_action = 'r_click'

        elif first_ring_l <= 15:
            last_action = 'start_input'

        else:
            # Declare default program status
            program_status.change_status('Moving Cursor')

        # Move virtual mouse
        if last_action == None or last_action == 'drag':
            moveMouse(frame, last_action, first_index_x, first_index_y)

    # Update program status window
    status_window.update()

    # Show window frame 
    cv2.imshow("Capturing Frame", frame)
    
    # Wait for 60 milliseconds and check if the key is 'esc'
    if cv2.waitKey(1) == 27:
        break

# Clear program status window
status_window.destroy()

# Clear video capture
cap.release()
cv2.destroyAllWindows()


