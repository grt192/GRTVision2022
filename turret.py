import cv2


class Turret:

    def __init__(self):
        self.hsv_lower = [0, 0, 250]
        self.hsv_upper = [200, 10, 255]

        self.hsv_frame = None
        self.mask = None
        self.result_frame = None

    # Returned frame must be same size as input frame
    def process(self, frame):
        self.hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        self.mask = cv2.inRange(self.hsv_frame, self.hsv_lower, self.hsv_upper)
        self.result_frame = cv2.bitwise_and(self.hsv_frame, self.hsv_frame, mask=self.mask)

        # TODO Use result_frame to find target coordinates

        # TODO Draw target on frame

        # TODO actually have data to pass
        data = {'test': 'turret test value!'}
        return frame, data
