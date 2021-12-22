import cv2
import time

# Rotate through the 4 USB ports until camera frames are obtained
input_port = 0
num_ports = 4

cap = None
img = None

while img is None:
    time.sleep(1)

    print("Error: No image to process. Cannot run vision pipeline. Are images being captured from the camera?")

    # Try to read the video stream
    cap = cv2.VideoCapture(input_port)
    _, img = cap.read()
    print("Trying /dev/video" + str(input_port))

    # Try the next port
    input_port = (input_port + 1) % num_ports

# Display stream
while cap.isOpened():
    _, img = cap.read()
    cv2.imshow('orig',img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
