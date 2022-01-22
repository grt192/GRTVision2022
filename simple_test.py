import threading
import logging
import time
from pipeline import Pipeline
from consumers.example_consumer import ExampleConsumer

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

print('Attempting add a MjpegServer with name ' + consumer.get_name())

# add mjpegserver to the cameraserver
# access at address mjpg:http://10.1.92.94:1181/?action=stream
server = cam_server.addServer(name=consumer.get_name())
print('Completed attempt to add server with name ' + consumer.get_name() + ' at port ' + str(server.getPort()))
stream = CvSource(consumer.get_name(), VideoMode.PixelFormat.kMJPEG, consumer.stream_res()[0], consumer.stream_res()[1], consumer.fps())
server.setSource(stream)
print('CvSource has been set for server ' + consumer.get_name() + ' at port ' + str(server.getPort()))

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    if ret:
        stream.putFrame(frame)

    time.sleep(0.1)


