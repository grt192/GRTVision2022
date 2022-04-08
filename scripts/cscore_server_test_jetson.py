import cv2
from cscore import CameraServer, CvSource, VideoMode
import time

device_num = '/dev/cam/turret'
server_name = 'generic server name'
source_width = 160
source_height = 120
source_fps = 30

cap = cv2.VideoCapture(device_num, cv2.CAP_V4L)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, source_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, source_height)

# Initialize a camera server
cam_server = CameraServer.getInstance()
cam_server.enableLogging()

# Add a camera server for the pipeline
print('Attempting add a MjpegServer with name ' + server_name)
server = cam_server.addServer(name=server_name)
print('Completed attempt to add server with name ' + server_name)
stream = CvSource(server_name, VideoMode.PixelFormat.kMJPEG, source_width, source_height, source_fps)
server.setSource(stream)
print('CvSource has been set for server ' + server_name + ' at port ' + str(server.getPort()))

while True:
    ret, frame = cap.read()
    if ret:
        stream.putFrame(frame)
    else:
        print('cannot capture')
        cap = cv2.VideoCapture(device_num, cv2.CAP_V4L)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, source_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, source_height)

    time.sleep(0.001)
