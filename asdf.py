# Find bounding box of the hub (ring)
# Make sure you know the width and height of the bounding box
# Find the coordinates for a) the middle of the right side of the rectangle and b) the middle of the left side
# Use both sets of coordinates to calculate 2 rays
# Find the angle between the two rays
# Use half of the angle, the radius of the hub, and do trig to get distance to the center of the hub


import math
import config
import numpy as np
import cv2

data = []
distances = []

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_EXPOSURE, -17)

# Vision constants
hsv_lower = np.array([0, 0, 250])
hsv_upper = np.array([200, 10, 255])

contour_min = 0
contour_max = 300

theta = math.pi / 8
r = 53.13 / 2  # inches

# 3D points in real world space
obj_points = np.array([[[r * math.cos(0), r * math.sin(0), 0],
                        [r * math.cos(theta), r * math.sin(theta), 0],
                        [r * math.cos(2 * theta), r * math.sin(2 * theta), 0],
                        [r * math.cos(3 * theta), r * math.sin(3 * theta), 0]]],
                      np.float32)

while True:

    ret, frame = cap.read()
    h, w, _ = frame.shape
    cam_x = int((w / 2) - 0.5)
    cam_y = int((h / 2) - 0.5)
    cam_center = (cam_x, cam_y)

    img = frame.copy()
    blur = cv2.blur(img, (4, 4))

    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, (0, 217, 28), (92, 255, 215))
    result = cv2.bitwise_and(frame, frame, mask=mask)

    # find all lemon contours in mask
    contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    numContours = 0
    output = []
    imagepoints = []

    if len(contours) != 0:
        for c in contours:
            M = cv2.moments(c)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
            else:
                cx, cy = 0, 0
            center = [cx, cy]
            output.append([c, cx, cy, center])
            imagepoints.append(center)

        output.sort(key=lambda x: x[1])
        imagepoints.sort(key=lambda x: x[0])
        if len(imagepoints) > 4:
            imagepoints = imagepoints[len(imagepoints) - 4:len(imagepoints)]
        if len(output) > 4:
            output = output[len(output) - 4:len(output)]

        for o in output:
            x, y, w, h = cv2.boundingRect(o[0])
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        imagepoints = np.array([imagepoints], np.float32)

        # Calibrate in real time

        try:
            retval, rvecs, tvecs = cv2.solveP3P(objectPoints=obj_points, imagePoints=imagepoints,
                                                cameraMatrix=config.newcameramtx, distCoeffs=None,
                                                flags=cv2.SOLVEPNP_P3P)
            print(len(rvecs))
        except:
            print("ERROR")
            continue

        # rvec to rotation matrix by axisangle to 3 by 3
        rmatrix, _ = cv2.Rodrigues(np.array([rvecs[0][0][0], rvecs[0][1][0], rvecs[0][2][0]], np.float32))
        transposed = rmatrix.T
        tmatrix = np.array([tvecs[0][0][0], tvecs[0][1][0], tvecs[0][2][0]], np.float32).reshape(3, 1)
        real_cam_center = np.matmul(-transposed, tmatrix)

        print("real_cam_center: ", real_cam_center)
        distances.append(real_cam_center[1][0])

        cv2.circle(frame, cam_center, 2, (0, 255, 0), -1)

    cv2.imshow('Original', frame)
    cv2.imshow('Mask', mask)

    key = cv2.waitKey(100)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()
