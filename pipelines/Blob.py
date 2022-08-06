import cv2
import numpy as np


class BlobDetector:

    def __init__(self, hsv_lower, hsv_upper, hsv_lower2=None, hsv_upper2=None):
        # Vision constants
        self.blur_radius = 6
        self.ksize_blur = int(6 * round(self.blur_radius) + 1)
        self.min_area = 20
        self.circularity = [0.0, 1.0]

        self.hsv_lower = hsv_lower
        self.hsv_upper = hsv_upper

        self.hsv_lower2 = None
        self.hsv_upper2 = None

        # Pre-allocated numpy arrays
        self.blur_frame = None
        self.hsv_frame = None
        self.mask1 = None
        self.mask2 = None
        self.mask = None
        self.canny_frame = None
        self.binary_frame = None
        self.circles = None


    def process(self, frame):
        output_value = 0

        # Blur
        self.blur_frame = cv2.GaussianBlur(frame, (self.ksize_blur, self.ksize_blur), round(self.blur_radius))

        # Convert to HSV
        self.hsv_frame = cv2.cvtColor(self.blur_frame, cv2.COLOR_BGR2HSV)

        # Color mask
        self.mask1 = cv2.inRange(self.hsv_frame, self.hsv_lower, self.hsv_upper)

        if self.hsv_lower2 is not None and self.hsv_upper2 is not None:
            self.mask2 = cv2.inRange(self.hsv_frame, self.hsv_lower2, self.hsv_upper2)
            self.mask = cv2.bitwise_or(self.mask1, self.mask2)
        else:
            self.mask = self.mask1

        # Canny edge
        self.canny_frame = cv2.Canny(self.mask, 200, 250)

        # Min and max circle radii
        w = frame.shape[0]
        h = frame.shape[1]
        min_radius = (int) (w / 12)
        max_radius = (int) (w / 2)

        # Hough circles
        self.circles = cv2.HoughCircles(self.canny_frame, cv2.HOUGH_GRADIENT, 1, (int) (w / 4), param1=254, param2=25,
                                        minRadius=min_radius, maxRadius=max_radius)

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
            output_value = len(self.circles)

        return output_value

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

