import cv2
from cscore import CameraServer, CvSource, VideoMode
import time
from pipelines.example_pipeline import ExamplePipeline


pipeline = ExamplePipeline('0', '/dev/cam/turret', False)
cap = None


# Initialize a camera server
cam_server = CameraServer.getInstance()
cam_server.enableLogging()


# Add a camera server for the pipeline
print('Attempting add a MjpegServer with name ' + pipeline.get_name())
server = cam_server.addServer(name=pipeline.get_name())
print('Completed attempt to add server with name ' + pipeline.get_name())
stream = CvSource(pipeline.server_name(), VideoMode.PixelFormat.kMJPEG, pipeline.stream_res()[0],
                  pipeline.stream_res()[1], pipeline.fps())
server.setSource(stream)
print('CvSource has been set for server ' + pipeline.server_name() + ' at port ' + str(server.getPort()))

cap = pipeline.get_capture()


while True:
    data, error_msg = pipeline.process()

    if error_msg is None:
        stream.putFrame(pipeline.get_frame())
    else:
        print('cannot capture ' + str(pipeline.get_device_num()))   

        time.sleep(0.001)
