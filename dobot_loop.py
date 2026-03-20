#!/usr/bin/env python3

import time
import pydobot

PORT = "/dev/ttyUSB0"

# Motion tuning (adjust slowly)
X_STEP = 20
Y_STEP = 20
Z_LIFT = 10

SPEED = 40
ACCEL = 40

PAUSE = 0.5


def main():
    device = None

    try:
        print("Connecting to Dobot...")
        device = pydobot.Dobot(port=PORT, verbose=True)

        device.speed(SPEED, ACCEL)

        x, y, z, r, *_ = device.pose()
        print(f"Start position: x={x:.2f}, y={y:.2f}, z={z:.2f}")

        print("\nStarting continuous loop (Ctrl+C to stop)...\n")

        while True:
            # Square pattern
            device.move_to(x + X_STEP, y, z, r, wait=True)
            time.sleep(PAUSE)

            device.move_to(x + X_STEP, y + Y_STEP, z, r, wait=True)
            time.sleep(PAUSE)

            device.move_to(x, y + Y_STEP, z, r, wait=True)
            time.sleep(PAUSE)

            device.move_to(x, y, z, r, wait=True)
            time.sleep(PAUSE)

            # Z up/down
            device.move_to(x, y, z + Z_LIFT, r, wait=True)
            time.sleep(PAUSE)

            device.move_to(x, y, z, r, wait=True)
            time.sleep(PAUSE)

    except KeyboardInterrupt:
        print("\nStopped by user.")

    except Exception as e:
        print("Error:", e)

    finally:
        if device is not None:
            try:
                device.close()
                print("Connection closed.")
            except:
                pass


if __name__ == "__main__":
    main()
