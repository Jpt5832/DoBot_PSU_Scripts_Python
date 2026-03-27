#!/usr/bin/env python3

import pydobot

PORT = "/dev/ttyUSB0"

# Movement step sizes
XY_STEP = 5.0
Z_STEP = 5.0
R_STEP = 5.0

# Safety limits
X_MIN, X_MAX = 150.0, 280.0
Y_MIN, Y_MAX = -120.0, 120.0
Z_MIN, Z_MAX = -20.0, 80.0
R_MIN, R_MAX = -90.0, 90.0

HOME_POS = (200.0, 0.0, 30.0, 0.0)

saved_corners = {
    "top_left": None,
    "top_right": None,
    "bottom_right": None,
    "bottom_left": None,
}


def clamp(value, low, high):
    return max(low, min(high, value))


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


def move_relative(device, dx=0.0, dy=0.0, dz=0.0, dr=0.0):
    x, y, z, r = get_pose(device)
    move_to_pose(device, x + dx, y + dy, z + dz, r + dr, wait=True)


def print_pose(device):
    x, y, z, r = get_pose(device)
    print(f"Current pose -> x={x:.1f}, y={y:.1f}, z={z:.1f}, r={r:.1f}")


def save_corner(device, name):
    x, y, z, r = get_pose(device)
    saved_corners[name] = (x, y)
    print(f"Saved {name}: ({x:.1f}, {y:.1f})")


def print_saved_corners():
    print("\nSaved robot paper corners:")
    for name in ["top_left", "top_right", "bottom_right", "bottom_left"]:
        print(f'  "{name}": {saved_corners[name]}')

    if all(saved_corners[name] is not None for name in saved_corners):
        print("\nCopy this into your main script:")
        print("ROBOT_PAPER_CORNERS = {")
        for name in ["top_left", "top_right", "bottom_right", "bottom_left"]:
            x, y = saved_corners[name]
            print(f'    "{name}": ({x:.1f}, {y:.1f}),')
        print("}")


def print_help():
    print("""
Controls:
  w  = move +X   (forward)
  s  = move -X   (backward)
  a  = move +Y   (left)
  d  = move -Y   (right)
  i  = move +Z   (up)
  k  = move -Z   (down)
  j  = rotate -R
  l  = rotate +R

  h  = go home
  p  = print current pose

  1  = save top_left
  2  = save top_right
  3  = save bottom_right
  4  = save bottom_left

  c  = print saved corners
  ?  = show help
  q  = quit
""")


def main():
    device = None
    try:
        device = pydobot.Dobot(port=PORT, verbose=True)
        print("Connected to DoBot.")
        print_help()
        move_to_pose(device, *HOME_POS, wait=True)

        while True:
            cmd = input("Command: ").strip().lower()

            if not cmd:
                continue

            if cmd == "q":
                print("Exiting...")
                break
            elif cmd == "?":
                print_help()
            elif cmd == "p":
                print_pose(device)
            elif cmd == "h":
                move_to_pose(device, *HOME_POS, wait=True)

            elif cmd == "w":
                move_relative(device, dx=XY_STEP)
            elif cmd == "s":
                move_relative(device, dx=-XY_STEP)
            elif cmd == "a":
                move_relative(device, dy=XY_STEP)
            elif cmd == "d":
                move_relative(device, dy=-XY_STEP)
            elif cmd == "i":
                move_relative(device, dz=Z_STEP)
            elif cmd == "k":
                move_relative(device, dz=-Z_STEP)
            elif cmd == "j":
                move_relative(device, dr=-R_STEP)
            elif cmd == "l":
                move_relative(device, dr=R_STEP)

            elif cmd == "1":
                save_corner(device, "top_left")
            elif cmd == "2":
                save_corner(device, "top_right")
            elif cmd == "3":
                save_corner(device, "bottom_right")
            elif cmd == "4":
                save_corner(device, "bottom_left")
            elif cmd == "c":
                print_saved_corners()
            else:
                print("Unknown command. Type ? for help.")

    finally:
        if device is not None:
            device.close()
            print("DoBot connection closed.")


if __name__ == "__main__":
    main()
