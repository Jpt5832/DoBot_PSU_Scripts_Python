#!/usr/bin/env python3

import tkinter as tk
import pydobot

PORT = "/dev/ttyUSB0"

STEP = 10
Z_STEP = 5
ROT_STEP = 5

SPEED = 50
ACCEL = 50


class DobotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Dobot Control GUI")

        print("Connecting to Dobot...")
        self.device = pydobot.Dobot(port=PORT, verbose=True)
        self.device.speed(SPEED, ACCEL)

        self.x, self.y, self.z, self.r, *_ = self.device.pose()

        # Position label
        self.label = tk.Label(root, text="", font=("Arial", 14))
        self.label.pack(pady=10)

        self.update_label()

        # Movement buttons
        frame = tk.Frame(root)
        frame.pack()

        # Row 1
        tk.Button(frame, text="↑ (W)", width=10, command=self.forward).grid(row=0, column=1)

        # Row 2
        tk.Button(frame, text="← (A)", width=10, command=self.left).grid(row=1, column=0)
        tk.Button(frame, text="→ (D)", width=10, command=self.right).grid(row=1, column=2)

        # Row 3
        tk.Button(frame, text="↓ (S)", width=10, command=self.back).grid(row=2, column=1)

        # Z controls
        tk.Button(root, text="Z UP", width=15, command=self.up).pack(pady=5)
        tk.Button(root, text="Z DOWN", width=15, command=self.down).pack(pady=5)

        # Rotation
        tk.Button(root, text="Rotate Left", width=15, command=self.rotate_left).pack(pady=5)
        tk.Button(root, text="Rotate Right", width=15, command=self.rotate_right).pack(pady=5)

        # Quit
        tk.Button(root, text="Quit", width=15, command=self.close).pack(pady=10)

    def update_label(self):
        self.label.config(text=f"x={self.x:.1f}, y={self.y:.1f}, z={self.z:.1f}, r={self.r:.1f}")

    def move(self):
        self.device.move_to(self.x, self.y, self.z, self.r, wait=True)
        self.update_label()

    def forward(self):
        self.y += STEP
        self.move()

    def back(self):
        self.y -= STEP
        self.move()

    def left(self):
        self.x -= STEP
        self.move()

    def right(self):
        self.x += STEP
        self.move()

    def up(self):
        self.z += Z_STEP
        self.move()

    def down(self):
        self.z -= Z_STEP
        self.move()

    def rotate_left(self):
        self.r -= ROT_STEP
        self.move()

    def rotate_right(self):
        self.r += ROT_STEP
        self.move()

    def close(self):
        print("Closing...")
        self.device.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = DobotGUI(root)
    root.mainloop()
