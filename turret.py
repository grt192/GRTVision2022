import cv2
import numpy

class Turret():

    hsv_lower = [0, 0, 250]
    hsv_upper = [200, 10, 255]

    def __init__():
        hsv_frame = None
        mask_frame = None
        result_frame = None


    # Returned frame must be same size as input frame
    def process(frame):

        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask_frame = cv2.inRange(hsv_frame, hsv_lower, hsv_upper)
        result_frame = cv2.bitwise_and(hsv_frame, hsv_frame, mask=mask_frame)

        # TODO Use result_frame to find target coordinates


        # TODO Draw target on frame


        # Return the frame
        return frame, data