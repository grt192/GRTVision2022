import threading
import time
import cv2


# Function to put values to NetworkTables
def send_to_network_table(roborio, data):

    for key, item in data.items():
        # https://robotpy.readthedocs.io/projects/pynetworktables/en/stable/api.html#networktables.NetworkTable.putValue
        # if list, check type and put array in NT
        if isinstance(item, list) or isinstance(item, tuple):
            if len(list) > 0:
                if isinstance(item[0], bool):
                    roborio.putBooleanArray(key, item)
                elif isinstance(item[0], int) or isinstance(item[0], float):
                    roborio.putNumberArray(key, item)
                elif isinstance(item[0], str):
                    roborio.putStringArray(key, item)
                else:
                    roborio.putRaw(key, item)
        else:
            # if not a list, put value and let NT auto-detect type
            roborio.putValue(key, item)


# Class to run pipeline
class PipelineThread(threading.Thread):
    def __init__(self, is_local, pipeline, roborio=None):
        threading.Thread.__init__(self)
        self.is_local = is_local
        self.pipeline = pipeline
        self.roborio = roborio

        if not is_local:
            from cscore import CameraServer, CvSource, VideoMode

            # Initialize a camera server
            cam_server = CameraServer.getInstance()
            cam_server.enableLogging()

            # Add a camera server for the pipeline
            print('Attempting add a MjpegServer with name ' + pipeline.get_name())
            server = cam_server.addServer(pipeline.get_name())
            print('Completed attempt to add server with name ' + pipeline.get_name())
            stream = CvSource(pipeline.get_name(), VideoMode.PixelFormat.kMJPEG, pipeline.get_resolution()[0], pipeline.get_resolution()[1], pipeline.get_fps())
            server.setSource(stream)
            print('CvSource has been set for server ' + pipeline.get_name() + ' at port ' + server.getPort())

            self.stream = stream

    def run(self):
        print('Starting thread running pipeline ' + self.pipeline.get_name())
        
        while True:
            # Process the next frame capture
            data, error_msg = self.pipeline.process()
            # If it doesn't work
            if error_msg is not None:
                print('Frame could not be processed: ' + error_msg)
            # If frame could be processed
            else:
                if self.is_local:
                    # print(data)
                    cv2.imshow(self.pipeline.get_name(), self.pipeline.get_frame())

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                else:
                    # Send data to robot
                    send_to_network_table(self.roborio, data)
                    # Put frame on output stream
                    self.stream.putFrame(self.pipeline.get_frame())

                    # Sleep the thread
                    time.sleep(0.001)

        print('Exiting thread running pipeline ' + self.pipeline.get_name())

