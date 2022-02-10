import cv2

class BlobDetector:
    def __init__(self, hsv_lower, hsv_upper):
        # Vision constants
        self.blur_radius = 6
        self.blob_min_area = 20
        self.blob_circularity = [0.0, 1.0]

        # Pre-allocated numpy arrays
        self.hsv_frame = None
        self.mask = None
        self.result_frame = None
        self.keypoints = None

    def process(self, frame):
        # Convert to HSV
        self.hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Color mask
        self.mask = cv2.inRange(self.hsv_frame, self.hsv_lower, self.hsv_upper)
        self.result_frame = cv2.bitwise_and(self.hsv_frame, self.hsv_frame, mask=self.mask)

        # Find blobs
        self.keypoints = self.find_blobs(self.result_frame)

        # TODO draw blobs

        # Return data
        return len(self.keypoints)

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
