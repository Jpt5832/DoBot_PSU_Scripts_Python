#!/usr/bin/env python3
 
import sys
import termios
import tty
import time
import pydobot
 
PORT = "/dev/ttyUSB0"
 
STEP = 10      # movement in mm
Z_STEP = 5
ROT_STEP = 5
 
SPEED = 50
ACCEL = 50
 
 
def get_key():
    """Read single keypress (Linux)"""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
 
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
 
    return ch
 
 
def main():
    device = None
 
    try:
        print("Connecting to Dobot...")
        device = pydobot.Dobot(port=PORT, verbose=True)
 
        device.speed(SPEED, ACCEL)
 
        x, y, z, r, *_ = device.pose()
 
        print("\n=== DOBOT KEYBOARD CONTROL ===")
        print("W/S = forward/back")
        print("A/D = left/right")
        print("R/F = up/down")
        print("Q/E = rotate")
        print("X   = exit")
        print("==============================\n")
 
        while True:
            print(f"Current: x={x:.1f}, y={y:.1f}, z={z:.1f}, r={r:.1f}")
            key = get_key()
 
            if key == 'w':
                y += STEP
            elif key == 's':
                y -= STEP
            elif key == 'a':
                x -= STEP
            elif key == 'd':
                x += STEP
            elif key == 'r':
                z += Z_STEP
            elif key == 'f':
                z -= Z_STEP
            elif key == 'q':
                r -= ROT_STEP
            elif key == 'e':
                r += ROT_STEP
            elif key == 'x':
                print("Exiting...")
                break
            else:
                continue
 
            print(f"Moving to x={x}, y={y}, z={z}, r={r}")
            device.move_to(x, y, z, r, wait=True)
            time.sleep(0.1)
 
    except KeyboardInterrupt:
        print("\nStopped.")
 
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
