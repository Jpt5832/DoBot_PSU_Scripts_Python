# DoBot Magician Python Scripts (Linux)

## How to Install (CLI)
1. git clone https://github.com/Jpt5832/DoBot_PSU_Scripts_Python.git
2. cd ~/DoBot_PSU_Scripts_Python

## How to run Scripts
1. cd ~/DoBot_PSU_Scripts_Python
2. source ~/dobot-venv/bin/activate (THIS IS IMPORTANT AND MUST BE RAN EVERY SESSION (Only run once) BEFORE ANY SCRIPTS)
3. python3 ~/dobot_gui.py (use whatever script file name here)

## How to run Gemini AI Scripts
1. install all required packages: pip3 install google-genai opencv-python pyserial pydobot pupil-apriltags
2. Generate Gemini API key using the link:

## Scripts Included
1. dobot_test.py: This is a very basic script to test small movement (only one or two moves for the robot)
2. dobot_loop.py: This loops what dobot_test.py does
3. dobot_keyboard.py: This script allows the user to control the robot via the keyboard (main keys are WASD, others: R,E,F,Z)
4. dobot_gui.py: This scripts allows the user to manually move the robot via a GUI

## Authors
1. PSU Cybersecurity Student - Jayson Troxel
2. PSU Cybersecurity Student - Mark Jachura
