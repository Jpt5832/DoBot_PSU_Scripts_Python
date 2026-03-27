#!/usr/bin/env python3

import os
import re
import time
import cv2
import pydobot
from google import genai

# ===== CONFIG =====
PORT = "/dev/ttyUSB0"
CAMERA_INDEX = 4
MODEL_NAME = "gemini-2.5-flash"

SAFE_APPROACH_OFFSET = 30
HOME_POS = (200, 0, 30, 0)

# Replace with your REAL measured coordinates
BLOCK_COORDS = {
    "red":    (220, -60, -35, 0),
    "blue":   (220, -20, -35, 0),
    "green":  (220,  20, -35, 0),
    "yellow": (220,  60, -35, 0),
}


# ===== GEMINI =====
def get_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set.")
    return genai.Client(api_key=api_key)


def ask_gemini_which_color(image_path: str) -> str:
    client = get_client()

    prompt = """
You are helping control a Dobot Magician robot arm.

Look at this image and decide which single colored block should be picked.

Return ONLY one word from this list:
red
blue
green
yellow
none

Rules:
- Return exactly one word.
- If no block is clearly visible, return none.
- Do not explain anything.
"""

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            prompt,
            {
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": image_bytes
                }
            }
        ]
    )

    text = (response.text or "").strip().lower()
    match = re.search(r"\b(red|blue|green|yellow|none)\b", text)
    return match.group(1) if match else "none"


# ===== WEBCAM =====
def capture_frame(filename="scene.jpg"):
    cap = cv2.VideoCapture(CAMERA_INDEX)

    if not cap.isOpened():
        raise RuntimeError(f"Could not open webcam at index {CAMERA_INDEX}")

    ok, frame = cap.read()
    cap.release()

    if not ok:
        raise RuntimeError(f"Could not read frame from camera {CAMERA_INDEX}")

    cv2.imwrite(filename, frame)
    return filename


# ===== DOBOT =====
def connect_dobot():
    return pydobot.Dobot(port=PORT, verbose=True)


def move_home(device):
    x, y, z, r = HOME_POS
    print("Going home...")
    device.move_to(x, y, z, r, wait=True)


def move_to_color(device, color):
    if color not in BLOCK_COORDS:
        print("Unknown color.")
        return

    x, y, z, r = BLOCK_COORDS[color]
    approach_z = z + SAFE_APPROACH_OFFSET

    print(f"Approaching {color} block...")
    device.move_to(x, y, approach_z, r, wait=True)
    time.sleep(0.5)

    print(f"Descending to {color} block...")
    device.move_to(x, y, z, r, wait=True)
    time.sleep(0.5)

    print("TODO: add gripper/suction here")

    # Lift back up safely
    device.move_to(x, y, approach_z, r, wait=True)


# ===== MAIN =====
def main():
    print(f"📷 Capturing image from camera index {CAMERA_INDEX}...")
    image_path = capture_frame()
    print(f"Saved image: {image_path}")

    print("🧠 Asking Gemini...")
    color = ask_gemini_which_color(image_path)
    print("Gemini selected:", color)

    if color == "none":
        print("No valid target detected. Exiting safely.")
        return

    device = None
    try:
        print("🔌 Connecting to DoBot...")
        device = connect_dobot()

        move_home(device)
        move_to_color(device, color)

        print("✅ Done.")

    finally:
        if device is not None:
            device.close()
            print("🔌 DoBot connection closed.")


if __name__ == "__main__":
    main()
