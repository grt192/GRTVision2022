import cv2
import time

# Rotate through the 4 USB ports until camera frames are obtained
input_port = 0
num_ports = 4

cap = None
img = None

g_str = ('gst-launch-1.0 -v v4l2src device=/dev/video{} !'
         'jpegdec !'
         'video/x-raw, framerate=(fraction){}/1, width=(int){}, height=(int){} !'
         'videoconvert !'
         'nvoverlaysink')

while img is None:
    time.sleep(1)

    print("Error: No image to process. Cannot run vision pipeline. Are images being captured from the camera?")

    # Try a different port
    input_port = (input_port + 1) % num_ports
    cap = cv2.VideoCapture(g_str.format(input_port, 30, 1920, 1080), cv2.CAP_GSTREAMER)
    _, img = cap.read()
    print("Trying /dev/video" + str(input_port))

# Display stream
while cap.isOpened():
    _, img = cap.read()
    cv2.imshow('orig',img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
