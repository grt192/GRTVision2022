import time

import cv2
import numpy as np
import threading

from consumers.consumer_interface import ConsumerInterface
from consumers.example_consumer import ExampleConsumer

'''
A full vision pipeline that, given a list of consumers, grabs frames, passes it 
to each consumer, and optionally streams a returned frame and saves data to a 
given network table.

This works by continuously checking to see if it is time for a consumer to 
process a frame. If so, it grabs a frame from that camera and passes it to every
consumer that needs the frame. Each consumer processes the frame, returning both 
an image to be streamed and a dictionary of values to be passed to a network 
table.

The pipeline stores cameras, consumers, streams, etc. in a dictionary. See 
self.cameras
'''


class Pipeline:

    # ms between each tick of the pipeline
    TICK_DELAY = 10

    '''
    Create and start a vision pipeline. 
    
    If no network_table is passed, this script will not attempt to use a network
    table or stream the camera sources. Instead, it will show the 'stream' frame
    from each consumer using opencv.
    '''
    def __init__(self, in_consumers, network_table=None):
        print("Pipeline initing...")

        self.connect = network_table != None
        self.network_table = network_table

        if self.connect:
            from cscore import CameraServer

            cam_server = CameraServer.getInstance()

        '''
        store all our cameras in a dictionary. 

        {
            <int (device number)>: 
                (
                    <cv2.VideoCapture>
                    , [
                        { # referred to as consumer_dict
                            'consumer': <consumers.ConsumerInterface>
                            , 'stream': <cscore.CvSource (stream)>
                            , 'last_process': <float>
                            , 'frame': <np.array (pre-allocated frame)>
                        }
                        , ...
                    ]
                )
            , ...
        }

        This pipeline setup recognizes that allocating new arrays, especially
        large ones, is extremely expensive. It tries to use the same 
        pre-allocated arrays, re-writing their values, as much as possible. 

        Consumers should try to do the same.
        '''
        self.cameras = {}

        for consumer in in_consumers:
            if not isinstance(consumer, ConsumerInterface):
                raise TypeError(
                    "Consumers to the vision pipeline must extend ConsumerInterface!")

            # if we're connected to a roborio (eg not running locally)
            # start streams for each consumer
            if self.connect:
                stream = cam_server.putVideo(
                    consumer.get_name(), consumer.stream_res()[0], consumer.stream_res()[1])
            else:
                stream = None

            consumer_dict = {
                'consumer': consumer,
                'stream': stream,
                'last_process': 0,
                'frame': None
            }

            # look to see if we've already inited a cam for this device num
            existing_camera = self.cameras.get(consumer.device_num())
            if existing_camera is None:
                camera = cv2.VideoCapture(consumer.device_num())

                self.cameras[consumer.device_num()] = (camera, [consumer_dict])
            else:
                existing_camera[1].append(consumer_dict)

    '''
    Start running the vision pipeline.
    '''
    def start(self):
        print("Starting!")

        last_tick = time.time() * 1000
        while True: # continuously check all consumers if they want a new frame
            current_time = time.time() * 1000

            if current_time >= last_tick + self.TICK_DELAY:
                # for each camera
                for device_num, info in self.cameras.items():
                    (capture, consumers) = info

                    # for each camera, have a variable that either shows
                    # we haven't gotten a frame yet (None)
                    # or is a reference to the frame we've got
                    frame_obj = None

                    # process each consumer for that camera
                    for consumer_dict in consumers:
                        consumer = consumer_dict.get('consumer')

                        # if it's time for that consumer to process again
                        if current_time > consumer_dict.get('last_process') + consumer.process_interval():
                            if frame_obj is None: # if we haven't gotten a frame from this camera this iteration
                                if consumer_dict.get('frame') is None:  # if the consumer doesn't have a pre-allocated array
                                    # let opencv give us a newly allocated frame
                                    ret, img = capture.read()
                                    consumer_dict['frame'] = img
                                else:
                                    # have opencv put the frame on our pre-allocated one for the consumer
                                    ret, img = capture.read(consumer_dict['frame'])

                                if ret is False:  # we got no frames
                                    print('empty frame?')
                                    break  # no sense processing a non-existent frame

                                # update our reference to match the latest frame
                                frame_obj = consumer_dict['frame']
                            else:  # we've already gotten a frame from this camera this iteration
                                if consumer_dict.get('frame') is None:  # the consumer doesn't have a pre-allocated frame obj yet
                                    # create a new np array
                                    # a copy of the frame we already grabbed
                                    consumer_dict['frame'] = np.copy(frame_obj)
                                else:
                                    # copy the frame we grabbed
                                    # to the already allocated frame array
                                    np.copyto(consumer_dict['frame'], frame_obj)

                            (to_stream, data) = consumer.process_frame(consumer_dict.get('frame'))

                            self.send_to_network_table(data)

                            if consumer_dict.get('stream') is not None:
                                consumer_dict.get('stream').putFrame(to_stream)
                            else:
                                # TODO remove this when we don't need to show anymore
                                cv2.imshow(consumer.get_name(), to_stream)

                            # save the latest update time to the tuple
                            consumer_dict['last_process'] = current_time

                last_tick = current_time

                # TODO remove this when we don't need to show anymore
                cv2.waitKey(1)

    def send_to_network_table(self, data):
        if not self.connect:
            return

        for key, item in data.items():
            # TODO this probably isn't good
            self.network_table.putValue(key, item)

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

if __name__ == '__main__':

    # Connect to NetworkTables 
    roborio = connect()

    # Start the pipeline
    pipeline = Pipeline([ExampleConsumer((300, 300), '0'),
                        ExampleConsumer((200, 400), '1')],
                        network_table=roborio)

    pipeline.start()