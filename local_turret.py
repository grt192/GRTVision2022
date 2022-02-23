'''
Since my computer seems to only be able to run one VideoCapture at once, turret and intake local testing scripts
are separated in two different scripts: local_turret.py and local_intake.py.
'''

import cv2
from turret import Turret

turret_cap = None


def init_cap():
    global turret_cap

    is_turret_cap = turret_cap is not None and turret_cap.isOpened()

    if not is_turret_cap:
        turret_cap = cv2.VideoCapture(1)
        turret_cap.set(cv2.CAP_PROP_EXPOSURE, -20)


# Init pipelines
turret = Turret()

while True:
    init_cap()

    # Run turret pipeline
    turret_vision_status = False
    turret_theta = 0
    hub_distance = 0

    ret, turret_frame = turret_cap.read()
    if ret:
        turret_frame = cv2.rotate(turret_frame, cv2.ROTATE_90_CLOCKWISE)

        turret_vision_status, turret_theta, hub_distance = turret.process(turret_frame)

        cv2.imshow("Turret", turret_frame)
        # cv2.imshow("Turret HSV", turret.hsv_frame)
        # cv2.imshow("Turret mask", turret.mask)

    print((turret_vision_status, turret_theta, hub_distance))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

turret_cap.release()
cv2.destroyAllWindows()
