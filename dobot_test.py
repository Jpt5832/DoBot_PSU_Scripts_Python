from serial.tools import list_ports
import pydobot
import time

# Detect available ports
ports = [p.device for p in list_ports.comports()]
print("Ports found:", ports)

# Set your Dobot port
port = "/dev/ttyUSB0"

# Connect to Dobot
device = pydobot.Dobot(port=port, verbose=True)

# Get current position
x, y, z, r, j1, j2, j3, j4 = device.pose()
print("Current pose:", x, y, z, r, j1, j2, j3, j4)

# Set speed (slow and safe)
device.speed(30, 30)

# Small safe movement test
device.move_to(x + 10, y, z, r, wait=True)
time.sleep(1)
device.move_to(x, y, z, r, wait=True)

# Close connection
device.close()
print("Done")
