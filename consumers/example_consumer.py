from re import I
import time

import cv2
import numpy as np

from consumers.consumer_interface import ConsumerInterface


class ExampleConsumer(ConsumerInterface):
    def __init__(self, center, name='0'):
        self.stream = None
        self.center = center
        self.name = name

    def process_frame(self, frame):
        if self.stream is None:
            self.stream = np.copy(frame)
        else:
            np.copyto(self.stream, frame)

        self.stream = cv2.circle(self.stream, self.center, 100, (0, 0, 255), 5)

        return (self.stream, {'test': 'test!'})

    def get_name(self):
        return self.name
