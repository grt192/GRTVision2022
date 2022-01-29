import cv2
from cscore import CameraServer, CvSource, VideoMode
import time

device_num = '/dev/cam/turret'
server_name = 'generic server name'
source_width = 160
source_height = 120
source_fps = 30

pipelines = [ExamplePipeline('0', '/dev/cam/turret', False), ExamplePipeline('1', '/dev/cam/intake', False)]
caps = []


# Initialize a camera server
cam_server = CameraServer.getInstance()
cam_server.enableLogging()

for pipeline in pipelines:

    # Add a camera server for the pipeline
    print('Attempting add a MjpegServer with name ' + pipeline.get_name())
    server = cam_server.addServer(name=pipeline.get_name())
    print('Completed attempt to add server with name ' + pipeline.get_name())
    stream = CvSource(pipeline.server_name(), VideoMode.PixelFormat.kMJPEG, pipeline.stream_res()[0], pipeline.stream_res()[1], pipeline.fps())
    server.setSource(stream)
    print('CvSource has been set for server ' + pipeline.server_name() + ' at port ' + str(server.getPort()))

    cap = pipeline.get_capture()

    caps.append(cap)

while True:
    for pipeline in pipelines:
        data, error_msg = pipeline.process()

        if error_msg is None:
            stream.putFrame(pipeline.get_frame())
        else:
            print('cannot capture')
            cap = pipeline.get_capture()

        time.sleep(0.001)
