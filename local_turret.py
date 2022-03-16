'''
Since my computer seems to only be able to run one VideoCapture at once, turret and intake local testing scripts
are separated in two different scripts: local_turret.py and local_intake.py.
'''

import cv2
from Turret import Turret
import numpy as np

turret_cap = None


def init_cap():
    global turret_cap

    is_turret_cap = turret_cap is not None and turret_cap.isOpened()

    if not is_turret_cap:
        turret_cap = cv2.VideoCapture(1)
        turret_cap.set(cv2.CAP_PROP_EXPOSURE, -10)


# Init pipelines
turret = Turret()



def nothing(x):
    pass


cv2.namedWindow("HSV Adjustments")
cv2.namedWindow("Contour Adjustments")

cv2.createTrackbar("Lower_H", "HSV Adjustments", 0, 255, nothing)
cv2.createTrackbar("Lower_S", "HSV Adjustments", 0, 255, nothing)
cv2.createTrackbar("Lower_V", "HSV Adjustments", 0, 255, nothing)
cv2.createTrackbar("Upper_H", "HSV Adjustments", 0, 255, nothing)
cv2.createTrackbar("Upper_S", "HSV Adjustments", 0, 255, nothing)
cv2.createTrackbar("Upper_V", "HSV Adjustments", 0, 255, nothing)

lower_arr = turret.hsv_lower
upper_arr = turret.hsv_upper
l_h = cv2.setTrackbarPos("Lower_H", "HSV Adjustments", lower_arr[0])
l_s = cv2.setTrackbarPos("Lower_S", "HSV Adjustments", lower_arr[1])
l_v = cv2.setTrackbarPos("Lower_V", "HSV Adjustments", lower_arr[2])
u_h = cv2.setTrackbarPos("Upper_H", "HSV Adjustments", upper_arr[0])
u_s = cv2.setTrackbarPos("Upper_S", "HSV Adjustments", upper_arr[1])
u_v = cv2.setTrackbarPos("Upper_V", "HSV Adjustments", upper_arr[2])


while True:
    init_cap()

    # Run turret pipeline
    turret_vision_status = False
    turret_theta = 0
    hub_distance = 0

    l_h = cv2.getTrackbarPos("Lower_H", "HSV Adjustments")
    l_s = cv2.getTrackbarPos("Lower_S", "HSV Adjustments")
    l_v = cv2.getTrackbarPos("Lower_V", "HSV Adjustments")
    u_h = cv2.getTrackbarPos("Upper_H", "HSV Adjustments")
    u_s = cv2.getTrackbarPos("Upper_S", "HSV Adjustments")
    u_v = cv2.getTrackbarPos("Upper_V", "HSV Adjustments")

    lower_bound = np.array([l_h, l_s, l_v])
    upper_bound = np.array([u_h, u_s, u_v])

    turret.set_hsv(lower_bound, upper_bound)


    ret, turret_frame = turret_cap.read()
    if ret:
        turret_frame = cv2.rotate(turret_frame, cv2.ROTATE_90_CLOCKWISE)

        turret_vision_status, turret_theta, hub_distance = turret.process(turret_frame)

        cv2.imshow("Turret", turret_frame)
        # cv2.imshow("Turret HSV", turret.hsv_frame)
        cv2.imshow("Turret mask", turret.mask)

    print((turret_vision_status, turret_theta, hub_distance))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

turret_cap.release()
cv2.destroyAllWindows()
