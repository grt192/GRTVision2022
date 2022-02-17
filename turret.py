import cv2
import numpy as np


class Turret:

    def __init__(self):
        self.hsv_lower = np.array([0, 0, 250])
        self.hsv_upper = np.array([200, 10, 255])

        self.hsv_frame = None
        self.mask = None
        self.result_frame = None

    # Returned frame must be same size as input frame. Draw on the given frame.
    def process(self, frame):
        self.hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        self.mask = cv2.inRange(self.hsv_frame, self.hsv_lower, self.hsv_upper)
        self.result_frame = cv2.bitwise_and(self.hsv_frame, self.hsv_frame, mask=self.mask)

        # TODO Use result_frame to find target coordinates

        # TODO Draw target on frame
        # temp test
        cv2.circle(frame, (50, 50), 50, (255, 0, 0))

        # TODO actually have data to pass
        turret_vision_status = False
        turret_theta = 0
        hub_distance = 0

        return turret_vision_status, turret_theta, hub_distance
