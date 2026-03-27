import cv2

CAMERA_INDEX = 4   # or 4

cap = cv2.VideoCapture(CAMERA_INDEX)
ok, frame = cap.read()
cap.release()

cv2.imwrite("final_test.jpg", frame)
print("Saved final_test.jpg")
