import cv2
from pupil_apriltags import Detector

CAMERA_INDEX = 4

cap = cv2.VideoCapture(CAMERA_INDEX)
detector = Detector(families="tag36h11")

print("Press ESC to quit.")

while True:
    ok, frame = cap.read()
    if not ok:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    tags = detector.detect(gray)

    for tag in tags:
        tag_id = tag.tag_id
        cx, cy = map(int, tag.center)
        print(f"Detected ID: {tag_id}")

        corners = tag.corners.astype(int)
        for i in range(4):
            p0 = tuple(corners[i])
            p1 = tuple(corners[(i + 1) % 4])
            cv2.line(frame, p0, p1, (0, 255, 0), 2)

        cv2.putText(
            frame,
            f"ID {tag_id}",
            (cx + 10, cy - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

    cv2.imshow("AprilTag IDs", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()
