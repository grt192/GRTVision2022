import numpy as np
from Blob import BlobDetector
import Utility


class Intake:

    def __init__(self):
        # Vision data
        self.ball_detected = False

        # Vision constants
        self.max_balls = 5
        self.min_balls = 1

        self.blue_hsv_lower = np.array([99, 71, 78])
        self.blue_hsv_upper = np.array([123, 255, 255])

        self.red_hsv_lower = np.array([0, 87, 0])
        self.red_hsv_upper = np.array([10, 255, 255])

        self.red_hsv_lower2 = np.array([170, 87, 0])
        self.red_hsv_upper2 = np.array([180, 255, 255])

        # Blob detectors
        self.blue_blob_detector = BlobDetector(self.blue_hsv_lower, self.blue_hsv_upper)
        self.red_blob_detector = BlobDetector(self.red_hsv_lower, self.red_hsv_upper, self.red_hsv_lower2,
                                              self.red_hsv_upper2)

    # Returned frame must be same size as input frame. Draw on the given frame.
    def process(self, frame):
        # Find blue blobs
        num_blue = self.blue_blob_detector.process(frame)

        # Find red blobs
        num_red = self.red_blob_detector.process(frame)

        if self.min_balls <= num_red + num_blue <= self.max_balls:
            self.ball_detected = True
        else:
            self.ball_detected = False

        # utility.put_text_group(frame, ('Balls? ' + str(self.ball_detected), ))

    def get_output_values(self):
        return (self.ball_detected, )  # return tuple
