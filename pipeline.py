from asyncio import current_task
import time
from typing import Type
from unicodedata import name
from consumers.example_consumer import ExampleConsumer

import numpy as np
import cv2

from consumers.consumer_interface import ConsumerInterface


class Pipeline:

    # ms between each tick of the pipeline
    TICK_DELAY = 10

    '''
    Create and start a vision pipeline. If no network_table is passed, this script will assume the script is running locally and not attempt to set up a network table or stream the camera source.
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
                        [
                            <consumers.ConsumerInterface>
                            , <cscore.CvSource (stream)>
                            , <float last_tick>
                            , <np.array (pre-allocated frame)>
                        ]
                        , ...
                    ]
                )
            , ...
        }
        '''
        self.cameras = {}

        for consumer in in_consumers:
            if not isinstance(consumer, ConsumerInterface):
                raise TypeError(
                    "Consumers to the vision pipeline must extend ConsumerInterface!")

            if self.connect:
                stream = cam_server.putVideo(
                    consumer.get_name(), consumer.stream_res()[0], consumer.stream_res()[1])
            else:
                stream = None

            consumer_tpl = [consumer, stream, 0, None]

            existing_camera = self.cameras.get(consumer.device_num())
            if existing_camera is None:
                camera = cv2.VideoCapture(consumer.device_num())

                self.cameras[consumer.device_num()] = (camera, [consumer_tpl])
            else:
                existing_camera[1].append(consumer_tpl)


    def start(self):
        print("Starting!")

        last_tick = time.time() * 1000
        while True:
            current_time = time.time() * 1000

            if current_time >= last_tick + self.TICK_DELAY:
                for device_num, info in self.cameras.items():
                    (capture, consumers) = info

                    frame_obj = None

                    # process each consumer for that camera
                    for tpl in consumers:
                        (consumer, stream, last_process, frame) = tpl

                        # if it's time for that consumer to process again
                        if current_time > last_process + consumer.process_interval():
                            if frame_obj is None:
                                if frame is None: # if there isn't a pre-allocated array
                                    ret, img = capture.read()

                                    frame = img
                                else:
                                    ret, img = capture.read(frame)

                                if ret is False: # we got no frames
                                    print('empty frame?')
                                    break # no sense processing a non-existent frame

                                frame_obj = frame
                            else:
                                if frame is None:
                                    frame = np.copy(frame_obj)
                                else:
                                    np.copyto(frame, frame_obj)

                            (to_stream, data) = consumer.process_frame(frame)

                            print(data)

                            self.send_to_network_table(data)

                            if stream is not None:
                                stream.putFrame(to_stream)
                            else:
                                print(to_stream.shape)
                                cv2.imshow(consumer.get_name(), to_stream)
                                cv2.waitKey(1)

                            tpl[2] = current_time

                last_tick = current_time

    def send_to_network_table(self, data):
        if not self.connect:
            return

        for key, item in data.items():
            # TODO this probably isn't good
            self.network_table.putValue(key, item)


if __name__ == '__main__':
    pipeline = Pipeline([ExampleConsumer()])

    pipeline.start()