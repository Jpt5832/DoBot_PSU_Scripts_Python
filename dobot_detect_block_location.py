#!/usr/bin/env python3

import cv2
import numpy as np
import time
import pydobot
from pupil_apriltags import Detector

# =========================
# CONFIG
# =========================
CAMERA_INDEX = 4
PORT = "/dev/ttyUSB0"

# Pick which color to target
TARGET_COLOR = "green"   # change to "red", "blue", or "yellow"

# Your AprilTag paper corners
CORNER_TAG_IDS = {
    302: "top_left",
    289: "top_right",
    290: "bottom_right",
    301: "bottom_left"
}

# Warped paper size in arbitrary units
PAGE_W = 850
PAGE_H = 1100

# Smoothing
ALPHA = 0.2
smoothed_centers = {
    "red": None,
    "green": None,
    "blue": None,
    "yellow": None
}

# Stability rule: require target to be seen this many frames before moving
REQUIRED_STABLE_FRAMES = 10

# DoBot calibration:
# These are the robot XY positions for the paper corners.
# YOU MUST TUNE THESE FOR YOUR SETUP.
#
# Example meaning:
# - top-left of paper    -> robot XY = (180,  80)
# - top-right of paper   -> robot XY = (260,  80)
# - bottom-right of paper-> robot XY = (260, -20)
# - bottom-left of paper -> robot XY = (180, -20)
#
# Adjust these after testing.
ROBOT_PAPER_CORNERS = {
    "top_left":     (180.0,  80.0),
    "top_right":    (260.0,  80.0),
    "bottom_right": (260.0, -20.0),
    "bottom_left":  (180.0, -20.0),
}

# Safe Z and R for moving above the paper
MOVE_Z = 20.0
MOVE_R = 0.0
HOME_POS = (200.0, 0.0, 30.0, 0.0)

# Safety limits
X_MIN, X_MAX = 150.0, 280.0
Y_MIN, Y_MAX = -120.0, 120.0
Z_MIN, Z_MAX = -20.0, 80.0
R_MIN, R_MAX = -90.0, 90.0


# =========================
# HELPERS
# =========================
def clamp(value, low, high):
    return max(low, min(high, value))


def order_points(pts_dict):
    return np.array([
        pts_dict["top_left"],
        pts_dict["top_right"],
        pts_dict["bottom_right"],
        pts_dict["bottom_left"]
    ], dtype=np.float32)


def smooth_point(color, x, y):
    global smoothed_centers

    if smoothed_centers[color] is None:
        smoothed_centers[color] = (x, y)
    else:
        old_x, old_y = smoothed_centers[color]
        new_x = (1 - ALPHA) * old_x + ALPHA * x
        new_y = (1 - ALPHA) * old_y + ALPHA * y
        smoothed_centers[color] = (new_x, new_y)

    return smoothed_centers[color]


def bilinear_map(norm_x, norm_y, corners):
    """
    Map normalized paper coords (0..1, 0..1) to robot XY using bilinear interpolation.
    corners:
      {
        "top_left": (x, y),
        "top_right": (x, y),
        "bottom_right": (x, y),
        "bottom_left": (x, y)
      }
    """
    tl = np.array(corners["top_left"], dtype=np.float32)
    tr = np.array(corners["top_right"], dtype=np.float32)
    br = np.array(corners["bottom_right"], dtype=np.float32)
    bl = np.array(corners["bottom_left"], dtype=np.float32)

    top = (1.0 - norm_x) * tl + norm_x * tr
    bottom = (1.0 - norm_x) * bl + norm_x * br
    point = (1.0 - norm_y) * top + norm_y * bottom

    return float(point[0]), float(point[1])


def connect_dobot():
    device = pydobot.Dobot(port=PORT, verbose=True)
    return device


def move_to_pose(device, x, y, z, r, wait=True):
    x = clamp(x, X_MIN, X_MAX)
    y = clamp(y, Y_MIN, Y_MAX)
    z = clamp(z, Z_MIN, Z_MAX)
    r = clamp(r, R_MIN, R_MAX)

    print(f"Moving DoBot to x={x:.1f}, y={y:.1f}, z={z:.1f}, r={r:.1f}")
    device.move_to(x, y, z, r, wait=wait)


def move_home(device):
    x, y, z, r = HOME_POS
    move_to_pose(device, x, y, z, r, wait=True)


def detect_color_block(color_name, mask, warped):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None

    largest = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(largest)

    if area < 500:
        return None

    x, y, w, h = cv2.boundingRect(largest)
    raw_cx = x + w / 2.0
    raw_cy = y + h / 2.0

    smooth_cx, smooth_cy = smooth_point(color_name, raw_cx, raw_cy)

    norm_x = smooth_cx / PAGE_W
    norm_y = smooth_cy / PAGE_H

    cv2.rectangle(warped, (x, y), (x + w, y + h), (0, 255, 255), 2)
    cv2.circle(warped, (int(raw_cx), int(raw_cy)), 5, (0, 0, 255), -1)
    cv2.circle(warped, (int(smooth_cx), int(smooth_cy)), 6, (255, 0, 255), -1)

    cv2.putText(
        warped,
        f"{color_name}: ({smooth_cx:.0f}, {smooth_cy:.0f})",
        (x, max(20, y - 10)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 0),
        2
    )

    return {
        "color": color_name,
        "raw_center": (raw_cx, raw_cy),
        "smooth_center": (smooth_cx, smooth_cy),
        "normalized": (norm_x, norm_y),
        "bbox": (x, y, w, h),
        "area": area
    }


# =========================
# MAIN
# =========================
def main():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        raise RuntimeError(f"Could not open camera at index {CAMERA_INDEX}")

    detector = Detector(families="tag36h11")
    kernel = np.ones((5, 5), np.uint8)

    dst_rect = np.array([
        [0, 0],
        [PAGE_W, 0],
        [PAGE_W, PAGE_H],
        [0, PAGE_H]
    ], dtype=np.float32)

    device = None
    moved_already = False
    stable_count = 0

    try:
        device = connect_dobot()
        print("Connected to DoBot")
        move_home(device)

        print("Press ESC to quit")

        while True:
            ok, frame = cap.read()
            if not ok:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            tags = detector.detect(gray)

            tag_centers = {}

            for tag in tags:
                if tag.tag_id in CORNER_TAG_IDS:
                    name = CORNER_TAG_IDS[tag.tag_id]
                    cx, cy = map(float, tag.center)
                    tag_centers[name] = (cx, cy)

                    corners = tag.corners.astype(int)
                    for i in range(4):
                        p0 = tuple(corners[i])
                        p1 = tuple(corners[(i + 1) % 4])
                        cv2.line(frame, p0, p1, (0, 255, 0), 2)

                    cv2.putText(
                        frame,
                        name,
                        (int(cx) + 10, int(cy) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (0, 255, 0),
                        2
                    )

            warped = None
            target_detection = None

            if all(k in tag_centers for k in ["top_left", "top_right", "bottom_right", "bottom_left"]):
                src = order_points(tag_centers)
                H = cv2.getPerspectiveTransform(src, dst_rect)
                warped = cv2.warpPerspective(frame, H, (PAGE_W, PAGE_H))

                cv2.putText(
                    frame,
                    "Paper detected",
                    (20, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 0, 0),
                    2
                )

                hsv = cv2.cvtColor(warped, cv2.COLOR_BGR2HSV)

                # Red
                red_lower1 = np.array([0, 120, 80])
                red_upper1 = np.array([10, 255, 255])
                red_lower2 = np.array([170, 120, 80])
                red_upper2 = np.array([180, 255, 255])

                # Green
                green_lower = np.array([40, 80, 80])
                green_upper = np.array([85, 255, 255])

                # Blue
                blue_lower = np.array([100, 100, 80])
                blue_upper = np.array([130, 255, 255])

                # Yellow
                yellow_lower = np.array([20, 100, 100])
                yellow_upper = np.array([35, 255, 255])

                red_mask1 = cv2.inRange(hsv, red_lower1, red_upper1)
                red_mask2 = cv2.inRange(hsv, red_lower2, red_upper2)
                red_mask = cv2.bitwise_or(red_mask1, red_mask2)

                green_mask = cv2.inRange(hsv, green_lower, green_upper)
                blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)
                yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)

                masks = {
                    "red": red_mask,
                    "green": green_mask,
                    "blue": blue_mask,
                    "yellow": yellow_mask,
                }

                cleaned_masks = {}
                detections = []

                for color_name, mask in masks.items():
                    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
                    cleaned_masks[color_name] = mask

                    result = detect_color_block(color_name, mask, warped)
                    if result is not None:
                        detections.append(result)

                # Show only target color data for movement
                target_detection = next((d for d in detections if d["color"] == TARGET_COLOR), None)

                if target_detection is not None:
                    sx, sy = target_detection["smooth_center"]
                    nx, ny = target_detection["normalized"]

                    robot_x, robot_y = bilinear_map(nx, ny, ROBOT_PAPER_CORNERS)

                    cv2.putText(
                        warped,
                        f"TARGET {TARGET_COLOR} -> norm=({nx:.2f},{ny:.2f})",
                        (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 255),
                        2
                    )

                    cv2.putText(
                        warped,
                        f"Robot XY=({robot_x:.1f},{robot_y:.1f})",
                        (20, 70),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 255),
                        2
                    )

                    print(
                        f"{TARGET_COLOR}: smooth=({sx:.1f},{sy:.1f}) "
                        f"norm=({nx:.2f},{ny:.2f}) "
                        f"robot=({robot_x:.1f},{robot_y:.1f})"
                    )

                    stable_count += 1
                else:
                    stable_count = 0

                cv2.imshow("Warped Paper", warped)
                cv2.imshow("Mask Red", cleaned_masks["red"])
                cv2.imshow("Mask Green", cleaned_masks["green"])
                cv2.imshow("Mask Blue", cleaned_masks["blue"])
                cv2.imshow("Mask Yellow", cleaned_masks["yellow"])

            else:
                stable_count = 0
                cv2.putText(
                    frame,
                    "Waiting for paper...",
                    (20, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (0, 0, 255),
                    2
                )

            cv2.imshow("Camera View", frame)

            # Move once after target is stable
            if (
                not moved_already
                and target_detection is not None
                and stable_count >= REQUIRED_STABLE_FRAMES
            ):
                nx, ny = target_detection["normalized"]
                robot_x, robot_y = bilinear_map(nx, ny, ROBOT_PAPER_CORNERS)

                print(f"Stable target found. Moving to {TARGET_COLOR} at robot XY=({robot_x:.1f},{robot_y:.1f})")
                move_to_pose(device, robot_x, robot_y, MOVE_Z, MOVE_R, wait=True)
                moved_already = True

            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                break
            elif key == ord("r"):
                moved_already = False
                stable_count = 0
                print("Reset movement lock. Ready to move again.")

    finally:
        cap.release()
        cv2.destroyAllWindows()
        if device is not None:
            device.close()
            print("DoBot connection closed.")


if __name__ == "__main__":
    main()
