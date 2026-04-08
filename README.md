# DoBot Magician Python Scripts (Linux)

## Overview
This repository contains Python scripts for controlling the DoBot Magician robotic arm on a Linux system. It includes both manual control scripts and AI-powered functionality using Google Gemini.

---

## Installation (CLI)

git clone https://github.com/Jpt5832/DoBot_PSU_Scripts_Python.git
cd ~/DoBot_PSU_Scripts_Python

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

---

## Running Gemini AI Scripts

### 1. Install Required Packages
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

- dobot_test.py  
  Basic test script for simple robot movements (1–2 actions)

- dobot_loop.py  
  Continuously loops the movements from dobot_test.py

- dobot_keyboard.py  
  Keyboard control for the robot  
  Main keys: W, A, S, D  
  Additional controls: R, E, F, Z

- dobot_gui.py  
  GUI-based manual control for the robot

---

## Authors

- Jayson Troxel — PSU Cybersecurity Student  
- Mark Jachura — PSU Cybersecurity Student
