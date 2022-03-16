import cv2
import numpy as np
import math
import Utility
import traceback


class Turret:

    def __init__(self):

        # Calibration camera matrices for the TURRET camera (error = 0.05089120586524974)
        # [[fx, 0, cx]
        #  [0, fy, cy]
        #  [0, 0, 1]]
        self.camera_mtx = np.array([[681.12589498, 0., 341.75575426],
                                    [0., 679.81937442, 202.55395243],
                                    [0., 0., 1.]])

        self.distortion = np.array([0.16170759, -1.11019546, -0.00809921, 0.00331081, 1.83787388])

        self.new_camera_mtx = np.array([[675.45861816, 0., 342.68931859],
                                        [0., 674.16143799, 199.02914604],
                                        [0., 0., 1.]])

        # Vision constants
        self.hsv_lower = np.array([36, 99, 20])
        self.hsv_upper = np.array([97, 255, 255])

        self.cam_center = None

        # Pre-allocated frames/arrays
        self.blur_frame = None
        self.hsv_frame = None
        self.mask = None

        self.masked_output = None
        self.output_frame = None

        # Data
        self.output_data = (False, 0, 0)


    # Returned frame must be same size as input frame. Draw on the given frame.
    def process(self, frame):
        temp_output_data = (False, 0, 0)

        # Get coordinates of the center of the frame
        if self.cam_center is None:
            h, w, _ = frame.shape
            cam_x = int((w / 2) - 0.5)
            cam_y = int((h / 2) - 0.5)
            self.cam_center = (cam_x, cam_y)

        # Draw reference lines (center line)
        h, w, _ = frame.shape
        cam_x = int((w / 2) - 0.5)
        cam_y = int((h / 2) - 0.5)
        cv2.line(frame, (0, cam_y), (w, cam_y),
                 (255, 255, 255), 2)

        # Blur
        # self.blur_frame = cv2.blur(frame, (4, 4))
        self.blur_frame = frame

        # Filter using HSV mask
        self.hsv_frame = cv2.cvtColor(self.blur_frame, cv2.COLOR_BGR2HSV)
        self.mask = cv2.inRange(self.hsv_frame, self.hsv_lower, self.hsv_upper)

        # Erode and dilate mask to remove tiny noise
        # Sometimes comment it out. Erode and dilate may cause tape blobs disappear and/or become two large --> ie they
        # become 1 contour instead of 4 distinct contours.
        # self.mask = cv2.erode(self.mask, None, iterations=1)
        # self.mask = cv2.dilate(self.mask, None, iterations=3)

        # self.mask = cv2.resize(self.mask, (0, 0), fx=0.25, fy=0.25)
        self.masked_output = np.copy(self.mask)

        # Grab contours
        contours = cv2.findContours(self.mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = grab_contours(contours)

        # Process contours
        output = []

        if len(contours) != 0:
            # Calculate center of each contour
            for c in contours:
                m = cv2.moments(c)
                if m["m00"] != 0:

                    cx = int(m["m10"] / m["m00"])
                    cy = int(m["m01"] / m["m00"])
                    center = [cx, cy]

                    # Append acceptable contours to list
                    output.append([c, cx, cy, center, cv2.contourArea(c)])

            # CONTOUR VALIDATION
            # Sort by area (descending)
            output.sort(key=lambda a: a[4], reverse=True)
            # print(len(output))

            # Take the 10 largest contours
            trunc_output = output[0:(10 if len(output) > 10 else len(output))]
            # print(len(trunc_output))
            filtered_output = []

            # Filter by: area, fullness, aspect ratio
            for o in trunc_output:

                x, y, w, h = cv2.boundingRect(o[0])
                # Draw bounding rectangles (1st round of filtering)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 127, 255), 1)  # orange

                # print('x, y, w, h', x, y, w, h)
                # print(o[4], o[4] / (w * h), h / w)

                # Is it large enough?
                if o[4] < 20:  # TODO test and check what min and max area should be +- 10%
                    continue

                # Does it fill at least 80% of its bounding rectangle?
                if o[4] < (w * h) * 0.5:
                    continue

                # Does it have a good aspect ratio?
                aspect_ratio = h / w  # Ideally greater than 1.5, less than 2.5
                if aspect_ratio < 1.5 or aspect_ratio > 4.5:
                    continue

                # Else, we've found a good contour!
                filtered_output.append(o)

                # Draw bounding rectangles (2nd round of filtering)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 1)  # red

            # print('f_o', len(filtered_output))

            filtered_output.sort(key=lambda a: a[4], reverse=True)

            final_contour = None
            if len(filtered_output) > 0:

                # filtered_output.sort(key=lambda a: frame[a[1], a[2]][1], reverse=True)  # sort by saturavation value of center pixel, descending
                final_contour = filtered_output[0]

            if final_contour is not None:
                # Draw the bounding box
                x, y, w, h = cv2.boundingRect(final_contour[0])
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)


                # print('x, y, w, h', x, y, w, h)
                # print('area, fullness, aspect ratio', final_contour[4], final_contour[4] / (w * h), h / w)

                final_contour_pos = (final_contour[1], final_contour[2])

                # Use interpolation to calculate distance
                distance = (36.75131166 * (math.e ** (0.002864827 * final_contour_pos[0]))) + 18.65849

                # Vision data to pass
                h, w, _ = frame.shape
                turret_vision_status = True
                turret_theta = (h / 2.0 + 0.5) - final_contour_pos[1]  # Return pixel distance
                hub_distance = distance

                cv2.circle(frame, final_contour_pos, 5, (255, 0, 0), 10)  # Blue

                temp_output_data = (turret_vision_status, turret_theta, hub_distance)

            # ax, d = self.get_ball_values_calib(frame, largest_cnt_pos)
            # ax, d = self.get_ball_values(frame, largest_cnt_pos)


        # Copy to the output frame
        # frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        self.output_frame = np.copy(frame)

        # Set output data
        self.output_data = temp_output_data


    def get_output_values(self):
        return self.output_data

    def get_output_frames(self):
        return [
            {
                'name': 'mask',
                'frame': self.masked_output
            },
            {
                'name': 'final',
                'frame': self.output_frame
            }
        ]

    def set_hsv(self, new_lower, new_upper):
        self.hsv_lower = new_lower
        self.hsv_upper = new_upper


    def get_ball_values_from_tvec(self, tvec):
        """ Ideally returns a distanc and pitch angle to target (ie. angle that the turret needs to rotate) but more
        extensive testing is needed. Seems to produce error just like the matrix multiplication operation does."""
        y = tvec[0][1][0]
        z = tvec[0][2][0]

        # Pythagorean theorem using y and z position (not x and z because target is rotated 90)
        a1 = math.atan2(y, z)
        d = math.sqrt(y ** 2 + z ** 2)

        print('a1, d', a1, d)

        return a1, d



    def get_ball_values(self, frame, center):
        '''Calculate the angle and distance from the camera to the center point of the robot
        This routine uses the FOV numbers and the default center to convert to normalized coordinates'''

        HFOV = 57.15  # horizontal angle of the field of view
        VFOV = 44.44  # vertical angle of the field of view

        # create imaginary view plane on 3d coords to get height and width
        # place the view place on 3d coordinate plane 1.0 unit away from (0, 0) for simplicity
        VP_HALF_WIDTH = math.tan(math.radians(HFOV) / 2.0)  # view plane 1/2 height
        VP_HALF_HEIGHT = math.tan(math.radians(VFOV) / 2.0)  # view plane 1/2 width

        shape = frame.shape

        tx = center[1]
        ty = center[0]

        # center is in pixel coordinates, 0,0 is the upper-left, positive down and to the right
        # (nx,ny) = normalized pixel coordinates, 0,0 is the center, positive right and up
        # WARNING: shape is (h, w, nbytes) not (w,h,...)
        image_w = shape[0] / 2.0
        image_h = shape[1] / 2.0

        # NOTE: the 0.5 is to place the location in the center of the pixel
        # print("center", center, "shape", shape)
        nx = (tx - image_w + 0.5) / image_w
        ny = (image_h - 0.5 - ty) / image_h

        # convert normal pixel coords to pixel coords
        x = VP_HALF_WIDTH * nx
        y = VP_HALF_HEIGHT * ny
        print("values", tx, ty, nx, ny, x, y)

        # now have all pieces to convert to angle:
        ax = math.atan2(x, 1.0)     # horizontal angle

        # naive expression
        # ay = math.atan2(y, 1.0)     # vertical angle

        # corrected expression.
        # As horizontal angle gets larger, real vertical angle gets a little smaller
        ay = math.atan2(y * math.cos(ax), 1.0)     # vertical angle
        # print("ax, ay", math.degrees(ax), math.degrees(ay))

        # now use the x and y angles to calculate the distance to the target:
        d = (self.target_height - self.camera_height) / math.tan(self.tilt_angle + ay)    # distance to the target

        print('using fov, ax, ay, d', math.degrees(ax), math.degrees(ay), d)

        return ax, d    # return horizontal angle and distance



    def get_ball_values_calib(self, frame, center):
        """Calculate the angle and distance from the camera to the center point of the robot
        This routine uses the cameraMatrix from the calibration to convert to normalized coordinates"""
        ''' Everything's in radians ig. Except for print statements '''

        # Swap target x and target y to account for hub being rotated 90
        tx = center[1]
        ty = center[0]

        h, w, _ = frame.shape
        cx = h / 2.0 + 0.5
        cy = w / 2.0 + 0.5


        # Swap fx and fy, cx and cy of the camera matrix
        # [[fx, 0, cx]
        #  [0, fy, cy]
        #  [0, 0, 1]]
        camera_mtx_rot = np.array([[679.81937442, 0., 202.55395243],
                                    [0., 681.12589498, 341.75575426],
                                    [0., 0., 1.]])

        print('tx, ty', tx, ty)
        print('cx, cy', camera_mtx_rot[0, 2], camera_mtx_rot[1, 2])
        print('cx, cy', cx, cy)

        self.target_height = 8 * 12 + 8  # inches
        self.camera_height = 28  # inches
        self.tilt_angle = math.radians(50)  # of camera

        cv2.circle(frame, (int(ty), int(tx)), 5, (255, 0, 0)) # blue
        cv2.circle(frame, (int(camera_mtx_rot[1, 2]), int(camera_mtx_rot[0, 2])), 5, (0, 255, 0))  # green
        cv2.circle(frame, (int(cy), int(cx)), 5, (0, 0, 255))  # red

        # x prime (along yaw to the hub. yes, yaw)
        # x_prime = (tx - camera_mtx_rot[0, 2]) / camera_mtx_rot[0, 0]
        # y (pitch to the hub)
        # y_prime = -(ty - camera_mtx_rot[1, 2]) / camera_mtx_rot[1, 1]

        # x prime (along yaw to the hub. yes, yaw)
        x_prime = (tx - cx) / camera_mtx_rot[0, 0]
        # y (pitch to the hub)
        print('ty, cy, camera_mtx[1, 1]', ty, cy, camera_mtx_rot[1,1])
        y_prime = -(ty - cy) / camera_mtx_rot[1, 1]

        print('x prime, y prime', x_prime, y_prime)

        # now have all pieces to convert to angle:
        ax = math.atan2(x_prime, 1.0)  # x horizontal angle (but actually yaw to hub)

        # naive expression
        # ay = math.atan2(y_prime, 1.0)  # y vertical angle (but actually pitch to the hub)

        # corrected expression.
        # As horizontal angle gets larger, real vertical angle gets a little smaller
        ay = math.atan2(y_prime * math.cos(ax), 1.0)     # vertical angle

        print('ax, ay', math.degrees(ax), math.degrees(ay))

        # now use the x and y angles to calculate the distance to the target:
        d = (self.target_height - self.camera_height) / math.tan(self.tilt_angle + ay)    # distance to the target
        print('d', d)
        return ax, d    # return angle to target (pitch) and distance


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
