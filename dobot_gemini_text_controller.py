#!/usr/bin/env python3

import os
import re
import time
import pydobot
from google import genai

PORT = "/dev/ttyUSB0"
MODEL_NAME = "gemini-2.5-flash"

# Safe step sizes
XY_STEP_SMALL = 15
XY_STEP_MED = 30
XY_STEP_LARGE = 50

Z_STEP_SMALL = 10
Z_STEP_MED = 20
Z_STEP_LARGE = 30

R_STEP_SMALL = 10
R_STEP_MED = 20
R_STEP_LARGE = 30

# Soft workspace limits - adjust for your setup
X_MIN, X_MAX = 150, 280
Y_MIN, Y_MAX = -120, 120
Z_MIN, Z_MAX = -20, 80
R_MIN, R_MAX = -90, 90

HOME_POS = (200, 0, 30, 0)


def clamp(value, low, high):
    return max(low, min(high, value))


def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set.")
    return genai.Client(api_key=api_key)


def ask_gemini(user_command: str) -> str:
    client = get_client()

    prompt = f"""
You are translating natural language into one safe Dobot command.

Return EXACTLY one line in one of these formats:

HOME
MOVE X +15
MOVE X -15
MOVE X +30
MOVE X -30
MOVE X +50
MOVE X -50
MOVE Y +15
MOVE Y -15
MOVE Y +30
MOVE Y -30
MOVE Y +50
MOVE Y -50
MOVE Z +10
MOVE Z -10
MOVE Z +20
MOVE Z -20
MOVE Z +30
MOVE Z -30
ROTATE +10
ROTATE -10
ROTATE +20
ROTATE -20
ROTATE +30
ROTATE -30
DEMO
NONE

Rules:
- Return only one command.
- Do not explain anything.
- If the request is unclear, unsafe, or asks for multiple unrelated things, return NONE.
- Map:
  - left/right to Y axis
  - forward/backward to X axis
  - up/down to Z axis
  - rotate left/right to ROTATE
  - go home/home position to HOME
  - short demo/demo sequence/wave/demo motion to DEMO

User request: {user_command}
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return (response.text or "").strip()


def connect_dobot():
    device = pydobot.Dobot(port=PORT, verbose=True)
    return device


def get_pose(device):
    pose = device.pose()

    try:
        x = float(pose[0])
        y = float(pose[1])
        z = float(pose[2])
        r = float(pose[3])
    except Exception:
        x = float(getattr(pose, "x"))
        y = float(getattr(pose, "y"))
        z = float(getattr(pose, "z"))
        r = float(getattr(pose, "r"))

    return x, y, z, r


def move_to_pose(device, x, y, z, r, wait=True):
    x = clamp(x, X_MIN, X_MAX)
    y = clamp(y, Y_MIN, Y_MAX)
    z = clamp(z, Z_MIN, Z_MAX)
    r = clamp(r, R_MIN, R_MAX)

    print(f"Moving to x={x:.1f}, y={y:.1f}, z={z:.1f}, r={r:.1f}")
    device.move_to(x, y, z, r, wait=wait)


def move_home(device):
    x, y, z, r = HOME_POS
    print("Going home...")
    move_to_pose(device, x, y, z, r, wait=True)


def move_relative(device, axis, delta):
    x, y, z, r = get_pose(device)
    print(f"Current pose: x={x:.1f}, y={y:.1f}, z={z:.1f}, r={r:.1f}")

    if axis == "X":
        x += delta
    elif axis == "Y":
        y += delta
    elif axis == "Z":
        z += delta
    else:
        print("Invalid axis.")
        return

    move_to_pose(device, x, y, z, r, wait=True)


def rotate_relative(device, delta):
    x, y, z, r = get_pose(device)
    print(f"Current pose: x={x:.1f}, y={y:.1f}, z={z:.1f}, r={r:.1f}")
    r += delta
    move_to_pose(device, x, y, z, r, wait=True)


def run_demo(device):
    print("Running demo sequence...")
    move_home(device)
    time.sleep(0.4)

    x, y, z, r = get_pose(device)

    move_to_pose(device, x, y - 30, z, r, wait=True)
    time.sleep(0.3)

    move_to_pose(device, x, y + 30, z, r, wait=True)
    time.sleep(0.3)

    move_to_pose(device, x, y, z + 20, r, wait=True)
    time.sleep(0.3)

    move_to_pose(device, x, y, z, r, wait=True)
    time.sleep(0.3)

    move_to_pose(device, x, y, z, r + 20, wait=True)
    time.sleep(0.3)

    move_to_pose(device, x, y, z, r - 20, wait=True)
    time.sleep(0.3)

    move_home(device)


def execute_command(device, command: str):
    command = command.strip().upper()
    print("Executing:", command)

    if command == "HOME":
        move_home(device)
        return

    if command == "DEMO":
        run_demo(device)
        return

    move_match = re.fullmatch(r"MOVE\s+([XYZ])\s+([+-]\d+)", command)
    if move_match:
        axis = move_match.group(1)
        delta = int(move_match.group(2))
        move_relative(device, axis, delta)
        return

    rotate_match = re.fullmatch(r"ROTATE\s+([+-]\d+)", command)
    if rotate_match:
        delta = int(rotate_match.group(1))
        rotate_relative(device, delta)
        return

    print("No valid safe command returned. No movement performed.")


def main():
    print("Gemini DoBot Controller Started")
    print("Try commands like:")
    print("  go home")
    print("  move left a little")
    print("  move forward")
    print("  move up")
    print("  rotate right")
    print("  do a short demo")
    print("Type 'exit' to quit.\n")

    device = None

    try:
        device = connect_dobot()
        print("Connected to DoBot.\n")

        while True:
            user_command = input("Enter Gemini AI command: ").strip()

            if not user_command:
                continue

            if user_command.lower() in ["exit", "quit", "q"]:
                print("Exiting...")
                break

            try:
                gemini_command = ask_gemini(user_command)
                print("Gemini returned:", gemini_command)

                if gemini_command.upper() == "NONE":
                    print("No action taken.\n")
                    continue

                execute_command(device, gemini_command)
                print()

            except Exception as e:
                print(f"Error: {e}\n")

    finally:
        if device is not None:
            device.close()
            print("DoBot connection closed.")


if __name__ == "__main__":
    main()
