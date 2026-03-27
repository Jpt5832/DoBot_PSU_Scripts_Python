import cv2
from pupil_apriltags import Detector
import math


def main():
    # Linux camera index
    cam_index = 4

    cap = cv2.VideoCapture(cam_index)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        raise RuntimeError(f"Could not open camera at index {cam_index}")

    detector = Detector(
        families="tag36h11",
        nthreads=2,
        quad_decimate=2.0,
        quad_sigma=0.0,
        refine_edges=1,
        decode_sharpening=0.25,
        debug=0
    )

    # Set this to the real printed tag size in meters
    tag_size_m = 0.152

    # Approximate intrinsics for now
    w, h = 1280, 720
    fx = 900.0
    fy = 900.0
    cx = w / 2.0
    cy = h / 2.0

    print("Press ESC to quit.")

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Failed to read frame.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        tags = detector.detect(
            gray,
            estimate_tag_pose=True,
            camera_params=(fx, fy, cx, cy),
            tag_size=tag_size_m
        )

        best = None
        if tags:
            best = max(tags, key=lambda t: t.decision_margin)

        if best is not None:
            tag_id = best.tag_id
            tx, ty, tz = best.pose_t.flatten().tolist()

            R = best.pose_R
            yaw = math.atan2(R[1, 0], R[0, 0])
            pitch = math.atan2(-R[2, 0], math.sqrt(R[2, 1]**2 + R[2, 2]**2))
            roll = math.atan2(R[2, 1], R[2, 2])
            roll, pitch, yaw = map(math.degrees, (roll, pitch, yaw))

            msg1 = f"ID: {tag_id}"
            msg2 = f"X: {tx:.3f} m  Y: {ty:.3f} m  Z: {tz:.3f} m"
            msg3 = f"roll: {roll:.1f}  pitch: {pitch:.1f}  yaw: {yaw:.1f}"

            cv2.putText(frame, msg1, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            cv2.putText(frame, msg2, (20, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            cv2.putText(frame, msg3, (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            corners = best.corners.astype(int)
            for i in range(4):
                p0 = tuple(corners[i])
                p1 = tuple(corners[(i + 1) % 4])
                cv2.line(frame, p0, p1, (0, 255, 0), 2)

            cx_tag, cy_tag = map(int, best.center)
            cv2.circle(frame, (cx_tag, cy_tag), 5, (0, 0, 255), -1)

            print(
                f"Tag ID={tag_id} | "
                f"X={tx:.3f}m Y={ty:.3f}m Z={tz:.3f}m | "
                f"roll={roll:.1f} pitch={pitch:.1f} yaw={yaw:.1f}"
            )

        cv2.imshow("AprilTag Pose (Linux)", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
