import numpy as np
from blob import BlobDetector

class Intake:

    def __init__(self):
        # Vision constants
        self.blue_hsv_lower = np.array([210, 200, 200])
        self.blue_hsv_upper = np.array([260, 255, 255])

        self.red_hsv_lower = np.array([0, 200, 200])
        self.red_hsv_upper = np.array([15, 255, 255])

        # Pre-allocated numpy arrays
        self.hsv_frame = None
        self.mask = None
        self.result_frame = None

        # Blob detectors
        self.blue_blob_detector = BlobDetector(self.blue_hsv_lower, self.blue_hsv_upper)
        self.red_blob_detector = BlobDetector(self.red_hsv_lower, self.red_hsv_upper)

    # Returned frame must be same size as input frame. Draw on the given frame.
    def process(self, frame):
        # Find blue blobs
        num_blue = self.blue_blob_detector.find_blobs(frame)

        if num_blue > 0:
            return True

        # Find red blobs
        num_red = self.red_blob_detector.find_blobs(frame)

        if num_red > 0:
            return True
