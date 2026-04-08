# DoBot Magician Python Scripts (Linux)

## Overview
This repository contains Python scripts for controlling the DoBot Magician robotic arm on a Linux system. It includes both manual control scripts and AI-powered functionality using Google Gemini.

---

## Installation (CLI)

- git clone https://github.com/Jpt5832/DoBot_PSU_Scripts_Python.git
- cd ~/DoBot_PSU_Scripts_Python

---

## Running Scripts

1. Navigate to the project directory:
cd ~/DoBot_PSU_Scripts_Python

2. Activate the virtual environment:
source ~/dobot-venv/bin/activate

⚠️ IMPORTANT: This must be run once per session before running any scripts.

3. Run a script:
python3 dobot_gui.py

Replace dobot_gui.py with any script name as needed.

4. ⚠️ NOTICE/IMPORTANT: You may have to change the PORT variable within the scripts for DoBot depending on which USB port the robot is connected to
Find what USB port the DoBot could be connected to (run one, or both ls commands):
- ls /dev/ttyUSB*
- ls /dev/ttyACM*

Once you found the port (one of the ls commands should output something like /dev/ttyACM0 or /dev/ttyUSB0), then:
1. nano {script_name}.py
2. Copy/Paste the port in the PORT variable
- Example: PORT = "/dev/ttyACM0"

---

## Running Gemini AI Scripts

### 1. Install Required Packages (if not already installed)
pip install google-genai opencv-python pyserial pydobot pupil-apriltags

---

### 2. Generate a Gemini API Key
Go to: https://aistudio.google.com/app/apikey  
Sign in with your Google account  
Click "Generate API Key" (top-right corner)

---

### 3. Set API Key (Environment Variable)

export GEMINI_API_KEY="PASTE_KEY_HERE"

Example:
export GEMINI_API_KEY="AIzaSyDK39f...abcd"

⚠️ IMPORTANT: This must be set every session (especially on public/shared machines).

---

### 4. Test Gemini Connection

python3 -c "from google import genai; client = genai.Client(); print(client.models.generate_content(model='gemini-2.0-flash', contents='Say exactly: Gemini is working').text)"

Expected output:
Gemini is working

---

### 5. Run Gemini Test Script

python3 dobot_gemini_text.py

- The script will prompt for a command  
- Example input: pick the yellow block  
- The robot will move to predefined coordinates for:
  - Yellow
  - Blue
  - Green
  - Red blocks  

Note: This version uses predefined positions (V1 implementation).

---

## Scripts Included

### Core Control Scripts
- **dobot_test.py**  
  Basic connection and movement test script used to verify communication with the DoBot and execute simple point-to-point movements.

- **dobot_loop.py**  
  Runs continuous movement loops for testing repeatability and motion sequences.

- **dobot_keyboard.py**  
  Allows real-time manual control of the robot using keyboard input (WASD + additional controls for vertical movement and rotation).

- **dobot_gui.py**  
  Graphical user interface (GUI) for controlling the robot arm interactively without using the terminal.

---

### AI + Gemini Integration
- **dobot_gemini_text_controller.py**  
  Integrates Google Gemini AI to interpret natural language commands (e.g., “move to the right by a little”) and convert them into robot movements.

- **dobot_gemini_webcam_colorblocks.py**  
  Uses a webcam along with Gemini AI and computer vision to detect colored blocks and move the robot to the correct position. (Not complete as of right now)

---

### Computer Vision & Detection
- **dobot_detect_block_location.py**  
  Detects block positions in the workspace and converts them into usable coordinates for the robot. (Coordinates aren't 100% stable)

- **block_on_paper.py**  
  Detects a single block placed on a defined surface (paper) and determines its position.

- **multiple_blocks_on_paper.py**  
  Extends block detection to handle multiple objects in the workspace.

- **webcam_test.py**  
  Tests webcam functionality and ensures video feed is working for vision-based scripts/generates test jpg file.

---

### AprilTag Integration
- **aprilTags_ID_Detector.py**  
  Detects AprilTags and identifies their IDs to assist with spatial positioning and tracking.

- **aprilTags_test.py**  
  Test script for verifying AprilTag detection and camera calibration.

---

### Calibration & Positioning
- **dobot_corner_calibration.py**  
  Calibrates workspace boundaries (corners) to map camera coordinates to robot coordinates. (Still a WIP)

- **quickcal.py**  
  Quick calibration utility for rapidly setting reference positions. (NOT USED)

---

### Miscellaneous
- **final_test.jpg**  
  Sample/test image used for webcam verification/image clarity.

## Authors

- Jayson Troxel — PSU Cybersecurity Student  
- Mark Jachura — PSU Cybersecurity Student
