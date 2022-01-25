import time
import cv2
import multiprocessing as mp
from pipelines.example_pipeline import ExamplePipeline
from pipelines.example_pipeline2 import ExamplePipeline2


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


# Function to run pipeline
def pipeline_process(event, is_local, pipeline, roborio=None, cam_server=None):
    
    if not is_local:
        from cscore import CvSource, VideoMode
        # Add a camera server for the pipeline
        print('Attempting add a MjpegServer with name ' + pipeline.get_name())
        server = cam_server.addServer(name=pipeline.get_name())
        print('Completed attempt to add server with name ' + pipeline.get_name())
        stream = CvSource(pipeline.get_name(), VideoMode.PixelFormat.kMJPEG, pipeline.stream_res()[0], pipeline.stream_res()[1], pipeline.fps())
        server.setSource(stream)
        print('CvSource has been set for server ' + pipeline.get_name() + ' at port ' + str(server.getPort()))


    print('Starting infinite loop running pipeline ' + pipeline.get_name())

    while not event.is_set():
        # Process the next frame capture
        data, error_msg = pipeline.process()
        # If it doesn't work
        if error_msg is not None:
            print('Frame could not be processed: ' + error_msg)
        # If frame could be processed
        else:
            if is_local:
                # print(data)
                cv2.imshow(pipeline.get_name(), pipeline.get_frame())

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            # If not local (on Jetson)
            else:
                # Send data to robot
                send_to_network_table(roborio, data)
                # Put frame on output stream
                stream.putFrame(pipeline.get_frame())

                # Sleep the thread
                time.sleep(0.001)

    # If the "terminate" event is triggered, exit
    print('Exiting thread running pipeline ' + pipeline.get_name())
    

def run_pipelines(is_local, pipelines, roborio=None):

    # Initialize a CameraServer (used by all pipelines)
    cam_server = None
    if not is_local:
        from cscore import CameraServer

        # Initialize a camera server
        cam_server = CameraServer.getInstance()
        cam_server.enableLogging()

    event = mp.Event()

    for pipeline in pipelines:
        # Create thread
        process = mp.Process(target=pipeline_process, args=(event, is_local, pipeline, roborio, cam_server))
        process.start()

    while True:
        try:
            pass
        except KeyboardInterrupt:
            print('Terminating processes...')
            event.set()
            print('Ending program...')
            break

if __name__ == '__main__':
    # Set process starting method (spawn is the only option for Windows)
    mp.set_start_method('spawn')
    pipelines = [ExamplePipeline('0'), ExamplePipeline2('1')]
    run_pipelines(True, pipelines)

