import cv2
import numpy as np


class BlobDetector:

    def __init__(self, hsv_lower, hsv_upper):
        # Vision constants
        self.blur_radius = 12
        self.ksize_blur = int(6 * round(self.blur_radius) + 1)
        self.min_area = 20
        self.circularity = [0.0, 1.0]

        self.hsv_lower = hsv_lower
        self.hsv_upper = hsv_upper

        # Pre-allocated numpy arrays
        self.blur_frame = None
        self.hsv_frame = None
        self.mask = None
        self.binary_frame = None
        self.circles = None

    def process(self, frame):
        # Blur
        self.blur_frame = cv2.GaussianBlur(frame, (self.ksize_blur, self.ksize_blur), round(self.blur_radius))

        # Convert to HSV
        self.hsv_frame = cv2.cvtColor(self.blur_frame, cv2.COLOR_BGR2HSV)

        # Color mask
        self.mask = cv2.inRange(self.hsv_frame, self.hsv_lower, self.hsv_upper)

        # Hough circles
        rows = self.mask.shape[0]
        self.circles = cv2.HoughCircles(self.mask, cv2.HOUGH_GRADIENT, 1, rows / 8, param1=200, param2=10, minRadius=0,
                                        maxRadius=0)

        # Draw circles
        if self.circles is not None:
            self.circles = np.uint16(np.around(self.circles))
            for i in self.circles[0, :]:
                center = (i[0], i[1])
                # circle center
                cv2.circle(frame, center, 1, (255, 0, 255), 3)
                # circle outline
                radius = i[2]
                cv2.circle(frame, center, radius, (255, 0, 255), 3)

            # Return data
            return len(self.circles)
        else:
            return 0

    def find_blobs(self, frame):
        params = cv2.SimpleBlobDetector_Params()
        params.filterByColor = 1
        params.blobColor = 255 # find white blobs
        params.minThreshold = 10
        params.maxThreshold = 220
        params.filterByArea = True
        params.minArea = self.min_area
        params.filterByCircularity = True
        params.minCircularity = self.circularity[0]
        params.maxCircularity = self.circularity[1]
        params.filterByConvexity = False
        params.filterByInertia = False
        detector = cv2.SimpleBlobDetector_create(params)

        return detector.detect(frame)
