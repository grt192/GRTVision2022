import cv2


class StaticImageSource:

    def __init__(self, image_path):
        self.image_path = image_path
        self.frame = None  # the image frame, pre-allocated to save memory

    def get_frame(self):
        self.frame = cv2.imread(cv2.samples.findFile(self.image_path))
        return self.frame


