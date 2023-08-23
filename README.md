# Virtual Mouse
A Python project that allows you to navigate your computer using your hands, just like a normal mouse. Left and right clicking functionalities are included, as well as dragging and typing through sign language.

## [Project Demo](/demo)

## Cloning the Repository
> Make sure to have the following modules installed: `opencv-python`, `mediapipe`, `pyautogui`, `tensorflow`, and `tkinter`.

1. Choose a preferred directory
2. Open a terminal and clone the repository: `git clone git@github.com:smgestupa/virtual-mouse.git`
3. Import the directory with your preferred IDE
4. Open a terminal in the project folder
5. Run the application with `python main.py`

## Instructions
- `Index Finger` will allow you to move your mouse across the screen
- Putting `Index Finger` and `Thumb Finger` together will do a left click
- Placing `Middle Finger` and `Thumb Finger` together will do a right click
- Placing `Ring Finger` and `Thumb Finger` will start the sign language detection process:
    - Requiring you to select an input field by left clicking (Putting `Index Finger` and `Thumb Finger` together)
    - After selecting an input field, place both of your hands in a place the `Capturing Frame` can see them
    - Your `Right Hand` will be used to gesture signs that the program can detect
    - Your `Left Hand` will be used to input characters: Open palm will input the characters, whilst a closed hand will not
    - Putting all or either of your hands for a few seconds will allow the program to return to its default state
