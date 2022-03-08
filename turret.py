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
                                        [0., 0., 1.]])

        # Vision constants
        self.hsv_lower = np.array([36, 99, 62])
        self.hsv_upper = np.array([97, 255, 255])

        self.cam_center = None

        # Pre-allocated frames/arrays
        self.blur_frame = None
        self.hsv_frame = None
        self.mask = None
        self.masked_frame = None

    # Returned frame must be same size as input frame. Draw on the given frame.
    def process(self, frame):

        # Init vision data
        turret_vision_status = False
        turret_theta = 0
        hub_distance = 0

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
        # Sometimes comment it out. Erode and dilate may cause tape blobs disappear and/or become two large --> ie they
        # become 1 contour instead of 4 distinct contours.
        self.mask = cv2.erode(self.mask, None, iterations=1)
        self.mask = cv2.dilate(self.mask, None, iterations=3)

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

                    # CONTOUR FILTERING
                    # Ignore tiny blobs of noise
                    # if cv2.contourArea(c) <= 5:
                        # print('Filtered out a tiny noise blob')
                        # continue
                    # _, _, w, h = cv2.boundingRect(c)

                    # Ignore contours that don't fill up much of their bounding rect
                    # if cv2.contourArea(c) < w * h * 0.75:
                        # print('Filtered out a blob w/ bad fill')
                        # continue

                    cx = int(m["m10"] / m["m00"])
                    cy = int(m["m01"] / m["m00"])
                    center = [cx, cy]

                    # Append acceptable contours to list
                    output.append([c, cx, cy, center])
                    image_points.append(center)


            # Sort output by center x of contour (ascending)
            output.sort(key=lambda a: a[1])

            # Sort image points by center x of contour
            image_points.sort(key=lambda a: a[0])

            # Reformat image_points array
            image_points = np.array(image_points, np.float32)

            print('# contours after filtering: ' + str(len(image_points)))
            '''
            if len(image_points) > 5:
                print("More than 5 tapes found, truncating to 4")
                image_points = image_points[len(image_points) - 4:len(image_points)]
                output = output[len(output) - 4:len(output)]
            '''

            # Draw bounding boxes for the contours
            for o in output:
                x, y, w, h = cv2.boundingRect(o[0])
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            try:
                # Check # of contours; sanity check
                if len(image_points) < 4 or len(image_points) > 5:
                    print("# contours is BAD; not 4 or 5")
                    raise

                print('Calculating hub dist...')
                # Else, calculate distance to hub
                obj_points = self.obj_points4

                if len(image_points) == 4:
                    print("4 points")
                    # Solve PNP with the 4 image points
                    _, rvecs, tvecs = cv2.solveP3P(objectPoints=obj_points, imagePoints=image_points,
                                                   cameraMatrix=self.new_camera_mtx, distCoeffs=self.distortion,
                                                   flags=cv2.SOLVEPNP_P3P)
                else:
                    print("5 points")

                    # Calculate a 4 image point array from 5 using midpoints of gaps between the tape pieces
                    new_image_points = np.zeros((4, 2), np.float32)

                    for i in range(3):
                        mid_x = (image_points[i][0] + image_points[i + 1][0]) / 2
                        mid_y = (image_points[i][1] + image_points[i + 1][1]) / 2
                        new_image_points[i, 0] = mid_x
                        new_image_points[i, 1] = mid_y
                    # Transfer new array over
                    image_points = np.array(new_image_points)

                    # Solve PNP
                    _, rvecs, tvecs = cv2.solveP3P(objectPoints=obj_points, imagePoints=image_points,
                                                   cameraMatrix=self.new_camera_mtx, distCoeffs=self.distortion,
                                                   flags=cv2.SOLVEPNP_P3P)

                print('Successfully solve PNPed')
                print('print rvecs for debugging angle calculation')
                print(rvecs)
                print('print tvecs')
                print(tvecs)

                # rvecs to rotation matrix by axis angle to 3 by 3
                rmatrix, _ = cv2.Rodrigues(np.array([rvecs[0][0][0], rvecs[0][1][0], rvecs[0][2][0]], np.float32))
                rmatrix_T = rmatrix.T
                tmatrix = np.array([tvecs[0][0][0], tvecs[0][1][0], tvecs[0][2][0]], np.float32).reshape(3, 1)
                real_cam_center = np.matmul(-rmatrix_T, tmatrix)

                # TODO Calculate turret theta (not actually an angle, more like pixel distance)
                # Calculate midpoint between leftmost and rightmost contour
                left_x = image_points[0][0]
                right_x = image_points[len(image_points) - 1][0]

                midpoint = (left_x + right_x) / 2

                # Vision data to pass
                turret_theta = midpoint - self.cam_center[0]
                turret_vision_status = True
                hub_distance = real_cam_center[1][0]

            except Exception as e:  # Leave if solvePNP doesn't work (ie. no contours detected)
                traceback.print_exc()
                print("Exception while finding contours")

        # Draw reference lines (center line)
        cv2.line(frame, (int(self.cam_center[0]), 0), (int(self.cam_center[0]), self.cam_center[1] * 2),
                 (255, 255, 255), 2)

        # Draw text
        # utility.put_text_group(frame, ('Status: ' + str(turret_vision_status),
        # 'Turret theta: ' + (str(turret_theta) if turret_vision_status else '---'),
        # 'Hub dist: ' + (str(hub_distance) if turret_vision_status else '---')))

        # Return vision data
        return turret_vision_status, turret_theta, hub_distance

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
