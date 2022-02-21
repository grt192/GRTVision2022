import cv2
import numpy as np
import math
import utility


class Turret:

    def __init__(self):

        # For vision processing
        theta = math.pi / 8  # radians
        r = 53.13 / 2  # inches
        # 3D points in real world space
        self.obj_points4 = np.array([[[r * math.cos(0), r * math.sin(0), 0],
                                 [r * math.cos(theta), r * math.sin(theta), 0],
                                 [r * math.cos(2 * theta), r * math.sin(2 * theta), 0],
                                 [r * math.cos(3 * theta), r * math.sin(3 * theta), 0]]], np.float32)

        theta_start = 3 * math.pi / 16

        self.obj_points5 = np.array([[[r * math.cos(theta_start), r * math.sin(theta_start), 0],
                                 [r * math.cos(theta_start + theta), r * math.sin(theta_start + theta), 0],
                                 [r * math.cos(theta_start + 2 * theta), r * math.sin(theta_start + 2 * theta), 0],
                                 [r * math.cos(theta_start + 3 * theta), r * math.sin(theta_start + 3 * theta), 0],
                                 [r * math.cos(theta_start + 4 * theta), r * math.sin(theta_start + 4 * theta), 0]]],
                               np.float32)

        # Calibration
        self.camera_mtx = np.array([[691.0036837, 0, 321.09540873],
                                   [0, 679.96569767, 211.53434312],
                                   [0, 0, 1]])

        self.distortion = np.array([0.10758992, -0.77644608, -0.00262037, -0.00947057,  1.16729517])

        self.new_camera_mtx = np.array([[683.24865723, 0, 315.31818897],
                                        [0, 667.2901001, 209.99858588],
                                        [0, 0, 1]])

        # Vision constants
        # TODO add HSV adjustment over TCP
        self.hsv_lower = np.array([0, 228, 16])
        self.hsv_upper = np.array([255, 255, 255])

        self.cam_center = None

        # Init vision data variables
        self.reset_data()

        # Pre-allocated frames
        self.blur_frame = None
        self.hsv_frame = None
        self.mask = None
        self.masked_frame = None

        self.rmatrix = None
        self.rmatrix_T = None
        self.tmatrix = None

    # Returned frame must be same size as input frame. Draw on the given frame.
    def process(self, frame):

        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

        # Get coordinates of the center of the frame
        if self.cam_center is None:
            h, w, _ = frame.shape
            cam_x = int((w / 2) - 0.5)
            cam_y = int((h / 2) - 0.5)
            self.cam_center = (cam_x, cam_y)

        # Blur
        self.blur_frame = cv2.blur(frame, (4, 4))

        # Filter using HSV mask
        self.hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        self.mask = cv2.inRange(self.hsv_frame, self.hsv_lower, self.hsv_upper)

        # Erode and dilate mask to remove tiny noise
        self.mask = cv2.erode(self.mask, None, iterations=5)
        self.mask = cv2.dilate(self.mask, None, iterations=10)

        self.masked_frame = cv2.bitwise_and(self.hsv_frame, self.hsv_frame, mask=self.mask)

        # Grab contours
        contours = cv2.findContours(self.mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = grab_contours(contours)

        # Process contours
        output = []
        image_points = []

        if len(contours) != 0:
            # Calculate center of each contour
            for c in contours:
                m = cv2.moments(c)
                if m["m00"] != 0:
                    cx = int(m["m10"] / m["m00"])
                    cy = int(m["m01"] / m["m00"])

                    center = [cx, cy]
                    # Array of contour and center
                    output.append([c, cx, cy, center])

                    image_points.append(center)

            # Sort output by center x of contour
            output.sort(key=lambda a: a[1])

            # Sort image points by center x of contour
            image_points.sort(key=lambda b: b[0])

            # Cut down the number of contours to either 4 or 5
            if len(image_points) > 5:
                image_points = image_points[len(image_points) - 4:len(image_points)]
                output = output[len(output) - 4:len(output)]

            # Draw bounding boxes for the contours
            for o in output:
                x, y, w, h = cv2.boundingRect(o[0])
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Reformat image_points array
            image_points = np.array([image_points], np.float32)

            # Calibrate in real time using rvecs and tvecs
            # Check the number of contours and use the appropriate obj_points

            try:
                # Sanity check
                if len(image_points) < 4 or len(image_points) > 5:
                    raise

                # Else, calculate distance to hub
                obj_points = self.obj_points4 if (len(image_points) == 4) else self.obj_points5
                _, rvecs, tvecs = cv2.solveP3P(objectPoints=obj_points, imagePoints=image_points,
                                               cameraMatrix=self.newcameramtx, distCoeffs=self.distortion,
                                               flags=cv2.SOLVEPNP_P3P)

                # rvecs to rotation matrix by axis angle to 3 by 3
                self.rmatrix, _ = cv2.Rodrigues(np.array([rvecs[0][0][0], rvecs[0][1][0], rvecs[0][2][0]], np.float32))
                self.rmatrix_T = self.rmatrix.T
                self.tmatrix = np.array([tvecs[0][0][0], tvecs[0][1][0], tvecs[0][2][0]], np.float32).reshape(3, 1)
                real_cam_center = np.matmul(-self.rmatrix_T, self.tmatrix)

                # Calculate turret theta (not actually an angle, more like pixel distance)
                # Calculate midpoint between leftmost and rightmost contour
                left_x = image_points[0][0]
                right_x = image_points[len(image_points) - 1][0]

                midpoint = (left_x + right_x) / 2
                self.turret_theta = midpoint - self.cam_center[0]

                # Vision data to pass
                self.turret_vision_status = True
                self.hub_distance = real_cam_center[1][0]


            except:  # Leave if solvePNP doesn't work (ie. no contours detected)
                print("ERROR while finding contours")
                self.reset_data()

        else:
            self.reset_data()

        # Draw reference lines (center line)
        cv2.line(frame, (int(self.cam_center[0]), 0), (int(self.cam_center[0]), self.cam_center[1] * 2), (255, 255, 255), 2)

        # Draw text
        utility.put_text_group(frame, ('Status: ' + str(self.turret_vision_status),
                                       'Turret theta: ' + (self.turret_theta if self.turret_vision_status else '---'),
                                       'Hub dist: ' + (self.hub_distance if self.turret_vision_status else '---')))

        # Return vision data
        return self.turret_vision_status, self.turret_theta, self.hub_distance

    # Initialize the vision data variables
    def reset_data(self):
        self.turret_vision_status = False
        self.turret_theta = 0
        self.hub_distance = 0



# Pulled from imutils package definition
def grab_contours(cnts):
    # if the length the contours tuple returned by cv2.findContours
    # is '2' then we are using either OpenCV v2.4, v4-beta, or
    # v4-official
    if len(cnts) == 2:
        cnts = cnts[0]

    # if the length of the contours tuple is '3' then we are using
    # either OpenCV v3, v4-pre, or v4-alpha
    elif len(cnts) == 3:
        cnts = cnts[1]

    # otherwise OpenCV has changed their cv2.findContours return
    # signature yet again and I have no idea WTH is going on
    else:
        raise Exception(("Contours tuple must have length 2 or 3, "
            "otherwise OpenCV changed their cv2.findContours return "
            "signature yet again. Refer to OpenCV's documentation "
            "in that case"))

    # return the actual contours array
    return cnts