import cv2


class TurretSource:

    def __init__(self, jetson=True):
        self.jetson = jetson
        self.cap = None  # VideoCapture object
        self.frame = None  # the image frame, pre-allocated to save memory

    def get_frame(self):

        # If the VideoCapture is not initialized
        if self.cap is None or (not self.cap.isOpened()):
            print('Trying to initialize turret cap...')

            if self.jetson:
                self.cap = cv2.VideoCapture('/dev/cam/turret', cv2.CAP_V4L)
                self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
                self.cap.set(cv2.CAP_PROP_EXPOSURE, 10)  # 5 to 2000
            else:
                self.cap = cv2.VideoCapture(0)
                self.cap.set(cv2.CAP_PROP_EXPOSURE, -10)

            # stream_res = (160, 120)
            # self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, stream_res[0])
            # self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, stream_res[1])

        _, self.frame = self.cap.read()

        return self.frame


