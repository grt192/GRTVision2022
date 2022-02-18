import numpy as np
from blob import BlobDetector


class Intake:

    def __init__(self):

        self.max_balls = 5
        self.min_balls = 1

        # Vision constants
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
            return True

        return False
