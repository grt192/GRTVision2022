import cv2
import logging


class IntakeSource:

    def __init__(self, jetson=True):
        self.jetson = jetson

        self.cap = None  # VideoCapture object
        self.frame = None  # the image frame, pre-allocated to save memory

    def get_frame(self):

        # If the VideoCapture is not initialized
        if self.cap is None or (not self.cap.isOpened()):
            logging.info('Trying to initialize intake cap...')

            if self.jetson:
                self.cap = cv2.VideoCapture('/dev/cam/intake', cv2.CAP_V4L)
            else:
                self.cap = cv2.VideoCapture(1)

            # stream_res = (160, 120)
            # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, stream_res[0])
            # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, stream_res[1])

        _, self.frame = self.cap.read()

        return self.frame


