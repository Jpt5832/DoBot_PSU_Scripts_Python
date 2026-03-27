import pydobot

device = pydobot.Dobot(port="/dev/ttyUSB0")

pose = device.pose()
print(pose)

device.close()
