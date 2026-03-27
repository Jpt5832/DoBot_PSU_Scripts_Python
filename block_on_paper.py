#!/usr/bin/env python3

import cv2
import numpy as np
from pupil_apriltags import Detector

CAMERA_INDEX = 4

# Your tag mapping
CORNER_TAG_IDS = {
    302: "top_left",
    289: "top_right",
    290: "bottom_right",
    301: "bottom_left"
}

# Paper size (arbitrary units)
PAGE_W = 850
PAGE_H = 1100

def order_points(pts_dict):
    return np.array([
        pts_dict["top_left"],
        pts_dict["top_right"],
        pts_dict["bottom_right"],
        pts_dict["bottom_left"]
    ], dtype=np.float32)

def main():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    detector = Detector(families="tag36h11")

    dst_rect = np.array([
        [0, 0],
        [PAGE_W, 0],
        [PAGE_W, PAGE_H],
        [0, PAGE_H]
    ], dtype=np.float32)

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
                    p1 = tuple(corners[(i+1)%4])
                    cv2.line(frame, p0, p1, (0,255,0), 2)

        H = None
        warped = None

        if all(k in tag_centers for k in ["top_left","top_right","bottom_right","bottom_left"]):
            src = order_points(tag_centers)
            H = cv2.getPerspectiveTransform(src, dst_rect)

            warped = cv2.warpPerspective(frame, H, (PAGE_W, PAGE_H))

            cv2.putText(frame, "Paper detected", (20,30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,0,0), 2)

        else:
            cv2.putText(frame, "Waiting for paper...", (20,30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)

        # ===== BLOCK DETECTION (COLOR BASED) =====
        if warped is not None:

            hsv = cv2.cvtColor(warped, cv2.COLOR_BGR2HSV)

            # ===== ADJUST THESE FOR YOUR BLOCK COLOR =====
            lower = np.array([0, 100, 100])
            upper = np.array([10, 255, 255])

            mask = cv2.inRange(hsv, lower, upper)

            # clean noise
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5,5)))

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                largest = max(contours, key=cv2.contourArea)

                if cv2.contourArea(largest) > 500:

                    x, y, w, h = cv2.boundingRect(largest)

                    cx = x + w/2
                    cy = y + h/2

                    # draw on warped view
                    cv2.rectangle(warped, (x,y), (x+w,y+h), (0,255,255), 2)
                    cv2.circle(warped, (int(cx), int(cy)), 5, (0,0,255), -1)

                    norm_x = cx / PAGE_W
                    norm_y = cy / PAGE_H

                    print(f"Block center: ({cx:.1f}, {cy:.1f}) | normalized: ({norm_x:.2f}, {norm_y:.2f})")

                    cv2.putText(warped,
                        f"({cx:.0f},{cy:.0f})",
                        (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        (255,255,0),
                        2)

            cv2.imshow("Warped Paper", warped)
            cv2.imshow("Mask", mask)

        cv2.imshow("Camera View", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
