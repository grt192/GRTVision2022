import threading
import cv2
import logging
import time

logging.basicConfig(level=logging.DEBUG)


# connect to NetworkTables
def connect():

    from networktables import NetworkTables

    # Start thread to connect to NetworkTables
    cond = threading.Condition()
    notified = [False]


    def connectionListener(connected, info):
        print(info, '; Connected=%s' % connected)
        with cond:
            notified[0] = True
            cond.notify()

    # Use RoboRIO static IP address
    # Don't use 'roborio-192-frc.local'. https://robotpy.readthedocs.io/en/stable/guide/nt.html#networktables-guide
    NetworkTables.initialize(server='10.1.92.2')
    NetworkTables.addConnectionListener(connectionListener, immediateNotify=True)

    with cond:
        print("Waiting")
        if not notified[0]:
            cond.wait()

    print("Connected to NetworkTables!")

    return NetworkTables.getTable('jetson')

roborio = connect()

from cscore import CameraServer, MjpegServer, CvSource, VideoMode

cam_server = CameraServer.getInstance()
cam_server.enableLogging()

print('Attempting add a MjpegServer with name ')

# add mjpegserver to the cameraserver
# access at address mjpg:http://10.1.92.94:1181/?action=stream
server = cam_server.addServer(name='name')
print('Completed attempt to add server with name at port ' + str(server.getPort()))
stream = CvSource('name', VideoMode.PixelFormat.kMJPEG, 16, 12, 10)
server.setSource(stream)
print('CvSource has been set for server at port ' + str(server.getPort()))

cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 120)

while True:
    ret, frame = cap.read()

    if ret:
        stream.putFrame(frame)
    else:
        cap = cv2.VideoCapture(1)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 120)
        print('trying to capture again')

    time.sleep(0.001)