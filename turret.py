import cv2
import numpy as np
import math
import utility
import traceback


class Turret:

    def __init__(self):

        # For vision processing
        theta = math.pi / 8  # radians
        r = 53.13 / 2  # inches
        # 3D points in real world space
        self.obj_points4 = np.array([[r * math.cos(0), r * math.sin(0), 0],
                                     [r * math.cos(theta), r * math.sin(theta), 0],
                                     [r * math.cos(2 * theta), r * math.sin(2 * theta), 0],
                                     [r * math.cos(3 * theta), r * math.sin(3 * theta), 0]], np.float32)

        theta_start = 3 * math.pi / 16

        self.obj_points5 = np.array([[r * math.cos(theta_start), r * math.sin(theta_start), 0],
                                     [r * math.cos(theta_start + theta), r * math.sin(theta_start + theta), 0],
                                     [r * math.cos(theta_start + 2 * theta), r * math.sin(theta_start + 2 * theta), 0],
                                     [r * math.cos(theta_start + 3 * theta), r * math.sin(theta_start + 3 * theta), 0],
                                     [r * math.cos(theta_start + 4 * theta), r * math.sin(theta_start + 4 * theta), 0]],
                                    np.float32)

        # Calibration camera matrices for the TURRET camera (error = 0.05089120586524974)
        self.camera_mtx = np.array([[681.12589498, 0., 341.75575426],
                                    [0., 679.81937442, 202.55395243],
                                    [0., 0., 1.]])

        self.distortion = np.array([0.16170759, -1.11019546, -0.00809921, 0.00331081, 1.83787388])

        self.new_camera_mtx = np.array([[675.45861816, 0., 342.68931859],
                                        [0., 674.16143799, 199.02914604],
                                        [0., 0., 1., ]])

        # Vision constants
        self.hsv_lower = np.array([36, 99, 62])
        self.hsv_upper = np.array([97, 255, 255])

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

        theta = math.pi / 8
        r = 53.13 / 2  # inches
        '''
        [r * math.cos(0), r * math.sin(0), 0],
        [r * math.cos(theta), r * math.sin(theta), 0],
        [r * math.cos(2 * theta), r * math.sin(2 * theta), 0],
        [r * math.cos(3 * theta), r * math.sin(3 * theta), 0]
        '''

        # TEMP draw
        # cv2.line(frame, (int(r * math.cos(0)), int(r * math.sin(0))), (int(r * math.cos(theta)), int(r * math.sin(theta))), (255, 255, 255), 2)
        # cv2.line(frame, (int(r * math.cos(2 * theta)), int(r * math.sin(2 * theta))), (int(r * math.cos(3 * theta)), int(r * math.sin(3 * theta))), (255, 255, 255), 2)

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
        self.mask = cv2.erode(self.mask, None, iterations=1)

        self.mask = cv2.dilate(self.mask, None, iterations=7)

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
            # TODO sort by area
            output.sort(key=lambda a: a[1])

            # Sort image points by center x of contour
            image_points.sort(key=lambda b: b[0])

            # Cut down the number of contours to either 4 or 5
            print(len(image_points))

            # Reformat image_points array
            image_points = np.array(image_points, np.float32)

            if len(image_points) > 5:
                print("trying to truncate")
                image_points = image_points[len(image_points) - 4:len(image_points)]
                output = output[len(output) - 4:len(output)]

            # Draw bounding boxes for the contours
            for o in output:
                x, y, w, h = cv2.boundingRect(o[0])
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Calibrate in real time using rvecs and tvecs
            # Check the number of contours and use the appropriate obj_points

            try:

                # Sanity check
                if len(image_points) < 4 or len(image_points) > 5:
                    print("length of contours array BAD")
                    # raise
                    self.reset_data()
                    return self.turret_vision_status, self.turret_theta, self.hub_distance

                print("sanity check passed")

                # Else, calculate distance to hub
                obj_points = self.obj_points4  # if (len(image_points) == 4) else self.obj_points5
                print(obj_points)
                print(len(obj_points))
                print(len(image_points))
                print(obj_points.shape)
                print(image_points.shape)

                if len(image_points) == 4:
                    print("4 pt img points ")
                    print(image_points)
                    _, rvecs, tvecs = cv2.solveP3P(objectPoints=obj_points, imagePoints=image_points,
                                                   cameraMatrix=self.new_camera_mtx, distCoeffs=self.distortion,
                                                   flags=cv2.SOLVEPNP_P3P)
                else:  # elif len(image_points) == 5:
                    print("length 5")

                    new_image_points = np.zeros((4, 2), np.float32)

                    for i in range(3):
                        mid_x = (image_points[i][0] + image_points[i + 1][0]) / 2
                        mid_y = (image_points[i][1] + image_points[i + 1][1]) / 2
                        new_image_points[i, 0] = mid_x
                        new_image_points[i, 1] = mid_y

                        print(str(mid_x) + ', ' + str(mid_y))

                    image_points = np.array(new_image_points)
                    print("5-pt image points: ")
                    print(image_points)

                    # TODO some potential issues: camera matrix (use the one from the turret camera), 90 degree rot??
                    # TODO 5 pt does not work
                    _, rvecs, tvecs = cv2.solveP3P(objectPoints=obj_points, imagePoints=image_points,
                                                   cameraMatrix=self.new_camera_mtx, distCoeffs=self.distortion,
                                                   flags=cv2.SOLVEPNP_P3P)

                print("-- made it here")

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

            except Exception as e:  # Leave if solvePNP doesn't work (ie. no contours detected)
                traceback.print_exc()
                print("ERROR while finding contours")
                self.reset_data()

        else:
            self.reset_data()

        # Draw reference lines (center line)
        cv2.line(frame, (int(self.cam_center[0]), 0), (int(self.cam_center[0]), self.cam_center[1] * 2),
                 (255, 255, 255), 2)

        # Draw text
        # utility.put_text_group(frame, ('Status: ' + str(self.turret_vision_status),
        # 'Turret theta: ' + (str(self.turret_theta) if self.turret_vision_status else '---'),
        # 'Hub dist: ' + (str(self.hub_distance) if self.turret_vision_status else '---')))

        # Return vision data
        return self.turret_vision_status, self.turret_theta, self.hub_distance

    # Initialize the vision data variables
    def reset_data(self):
        self.turret_vision_status = False
        self.turret_theta = 0
        self.hub_distance = 0

    def set_hsv(self, new_lower, new_upper):
        self.hsv_lower = new_lower
        self.hsv_upper = new_upper


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
