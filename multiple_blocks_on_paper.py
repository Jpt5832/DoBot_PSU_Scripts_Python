#!/usr/bin/env python3

import cv2
import numpy as np
from pupil_apriltags import Detector

CAMERA_INDEX = 4

CORNER_TAG_IDS = {
    302: "top_left",
    289: "top_right",
    290: "bottom_right",
    301: "bottom_left"
}

PAGE_W = 850
PAGE_H = 1100

ALPHA = 0.2  # smoothing factor

# Smoothed centers for each color
smoothed_centers = {
    "red": None,
    "green": None,
    "blue": None,
    "yellow": None
}


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


def detect_color_block(hsv, warped, color_name, mask):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None

    largest = max(contours, key=cv2.contourArea)

    if cv2.contourArea(largest) < 500:
        return None

    x, y, w, h = cv2.boundingRect(largest)
    raw_cx = x + w / 2
    raw_cy = y + h / 2

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
        "bbox": (x, y, w, h)
    }


def main():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        raise RuntimeError(f"Could not open camera at index {CAMERA_INDEX}")

    detector = Detector(families="tag36h11")

    dst_rect = np.array([
        [0, 0],
        [PAGE_W, 0],
        [PAGE_W, PAGE_H],
        [0, PAGE_H]
    ], dtype=np.float32)

    kernel = np.ones((5, 5), np.uint8)

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
                    f"{name}",
                    (int(cx) + 10, int(cy) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )

        warped = None

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
        else:
            cv2.putText(
                frame,
                "Waiting for paper...",
                (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )

        if warped is not None:
            hsv = cv2.cvtColor(warped, cv2.COLOR_BGR2HSV)

            # ----- COLOR MASKS -----

            # Red needs two ranges
            red_lower1 = np.array([0, 120, 80])
            red_upper1 = np.array([10, 255, 255])
            red_lower2 = np.array([170, 120, 80])
            red_upper2 = np.array([180, 255, 255])

            green_lower = np.array([40, 80, 80])
            green_upper = np.array([85, 255, 255])

            blue_lower = np.array([100, 100, 80])
            blue_upper = np.array([130, 255, 255])

            yellow_lower = np.array([20, 100, 100])
            yellow_upper = np.array([35, 255, 255])

            red_mask1 = cv2.inRange(hsv, red_lower1, red_upper1)
            red_mask2 = cv2.inRange(hsv, red_lower2, red_upper2)
            red_mask = cv2.bitwise_or(red_mask1, red_mask2)

            green_mask = cv2.inRange(hsv, green_lower, green_upper)
            blue_mask = cv2.inRange(hsv, blue_lower, blue_upper)
            yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)

            # Clean masks
            red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_OPEN, kernel)
            red_mask = cv2.morphologyEx(red_mask, cv2.MORPH_CLOSE, kernel)

            green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_OPEN, kernel)
            green_mask = cv2.morphologyEx(green_mask, cv2.MORPH_CLOSE, kernel)

            blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_OPEN, kernel)
            blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_CLOSE, kernel)

            yellow_mask = cv2.morphologyEx(yellow_mask, cv2.MORPH_OPEN, kernel)
            yellow_mask = cv2.morphologyEx(yellow_mask, cv2.MORPH_CLOSE, kernel)

            detections = []

            for color_name, mask in [
                ("red", red_mask),
                ("green", green_mask),
                ("blue", blue_mask),
                ("yellow", yellow_mask)
            ]:
                result = detect_color_block(hsv, warped, color_name, mask)
                if result is not None:
                    detections.append(result)

            for d in detections:
                sx, sy = d["smooth_center"]
                nx, ny = d["normalized"]
                print(f'{d["color"]}: center=({sx:.1f}, {sy:.1f}) norm=({nx:.2f}, {ny:.2f})')

            cv2.imshow("Warped Paper", warped)
            cv2.imshow("Mask Red", red_mask)
            cv2.imshow("Mask Green", green_mask)
            cv2.imshow("Mask Blue", blue_mask)
            cv2.imshow("Mask Yellow", yellow_mask)

        cv2.imshow("Camera View", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
