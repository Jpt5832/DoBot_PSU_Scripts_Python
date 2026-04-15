#!/usr/bin/env python3
 
import sys
import tkinter as tk
 
try:
    import pygame
except ImportError:
    print("pygame is required. Install it with: pip install pygame")
    sys.exit(1)
 
try:
    import pydobot
except ImportError:
    print("pydobot is required. Install it with: pip install pydobot")
    sys.exit(1)
 
PORT = "/dev/ttyUSB0"
 
STEP = 25
Z_STEP = 5
ROT_STEP = 5
SPEED = 50
ACCEL = 50
DEADZONE = 0.35
POLL_MS = 120
 
 
class DobotXboxGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Dobot + Xbox Controller")
 
        self.last_input = {
            "left": False,
            "right": False,
            "up": False,
            "down": False,
            "z_up": False,
            "z_down": False,
            "rot_left": False,
            "rot_right": False,
        }
 
        self.status_text = tk.StringVar(value="Starting...")
 
        print("Connecting to Dobot...")
        self.device = pydobot.Dobot(port=PORT, verbose=True)
        self.device.speed(SPEED, ACCEL)
        self.x, self.y, self.z, self.r, *_ = self.device.pose()
 
        pygame.init()
        pygame.joystick.init()
 
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            controller_name = self.joystick.get_name()
            self.status_text.set(f"Controller connected: {controller_name}")
            print(f"Controller detected: {controller_name}")
        else:
            self.status_text.set("No controller detected. GUI controls still work.")
            print("No controller detected")
 
        self.position_label = tk.Label(root, text="", font=("Arial", 14))
        self.position_label.pack(pady=10)
 
        self.status_label = tk.Label(root, textvariable=self.status_text, font=("Arial", 11))
        self.status_label.pack(pady=5)
 
        self.update_label()
 
        frame = tk.Frame(root)
        frame.pack()
 
        tk.Button(frame, text="↑ (W)", width=10, command=self.forward).grid(row=0, column=1)
        tk.Button(frame, text="← (A)", width=10, command=self.left).grid(row=1, column=0)
        tk.Button(frame, text="→ (D)", width=10, command=self.right).grid(row=1, column=2)
        tk.Button(frame, text="↓ (S)", width=10, command=self.back).grid(row=2, column=1)
 
        tk.Button(root, text="Z UP", width=15, command=self.up).pack(pady=5)
        tk.Button(root, text="Z DOWN", width=15, command=self.down).pack(pady=5)
        tk.Button(root, text="Rotate Left", width=15, command=self.rotate_left).pack(pady=5)
        tk.Button(root, text="Rotate Right", width=15, command=self.rotate_right).pack(pady=5)
        tk.Button(root, text="Quit", width=15, command=self.close).pack(pady=10)
 
        instructions = (
            "Xbox mapping:\n"
            "Left stick = X/Y movement\n"
            "Right stick up/down = Z movement\n"
            "Right stick left/right = rotation\n"
            "D-pad also works for X/Y movement"
        )
        tk.Label(root, text=instructions, justify="left", font=("Arial", 10)).pack(pady=8)
 
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.poll_controller()
 
    def update_label(self):
        self.position_label.config(
            text=f"x={self.x:.1f}, y={self.y:.1f}, z={self.z:.1f}, r={self.r:.1f}"
        )
 
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
 
    def _pressed_once(self, key, pressed):
        previous = self.last_input[key]
        self.last_input[key] = pressed
        return pressed and not previous
 
    def poll_controller(self):
        if self.joystick is not None:
            pygame.event.pump()
 
            axis_0 = self.joystick.get_axis(0) if self.joystick.get_numaxes() > 0 else 0.0
            axis_1 = self.joystick.get_axis(1) if self.joystick.get_numaxes() > 1 else 0.0
            axis_3 = self.joystick.get_axis(3) if self.joystick.get_numaxes() > 3 else 0.0
            axis_4 = self.joystick.get_axis(4) if self.joystick.get_numaxes() > 4 else 0.0
 
            hat_x, hat_y = (0, 0)
            if self.joystick.get_numhats() > 0:
                hat_x, hat_y = self.joystick.get_hat(0)
 
            left_pressed = axis_0 < -DEADZONE or hat_x == -1
            right_pressed = axis_0 > DEADZONE or hat_x == 1
            forward_pressed = axis_1 < -DEADZONE or hat_y == 1
            back_pressed = axis_1 > DEADZONE or hat_y == -1
            rot_left_pressed = axis_3 < -DEADZONE
            rot_right_pressed = axis_3 > DEADZONE
            z_up_pressed = axis_4 < -DEADZONE
            z_down_pressed = axis_4 > DEADZONE
 
            if self._pressed_once("left", left_pressed):
                self.left()
            if self._pressed_once("right", right_pressed):
                self.right()
            if self._pressed_once("up", forward_pressed):
                self.forward()
            if self._pressed_once("down", back_pressed):
                self.back()
            if self._pressed_once("rot_left", rot_left_pressed):
                self.rotate_left()
            if self._pressed_once("rot_right", rot_right_pressed):
                self.rotate_right()
            if self._pressed_once("z_up", z_up_pressed):
                self.up()
            if self._pressed_once("z_down", z_down_pressed):
                self.down()
 
        self.root.after(POLL_MS, self.poll_controller)
 
    def close(self):
        print("Closing...")
        try:
            if self.joystick is not None:
                self.joystick.quit()
            pygame.joystick.quit()
            pygame.quit()
        except Exception:
            pass
 
        try:
            self.device.close()
        except Exception:
            pass
 
        self.root.destroy()
 
 
if __name__ == "__main__":
    root = tk.Tk()
    app = DobotXboxGUI(root)
    root.mainloop()
