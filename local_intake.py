'''
Since my computer seems to only be able to run one VideoCapture at once, turret and intake local testing scripts
are separated in two different scripts: local_turret.py and local_intake.py.
'''

import cv2
from intake import Intake


intake_cap = None


def init_cap():
    global intake_cap

    is_intake_cap = intake_cap is not None and intake_cap.isOpened()

    if not is_intake_cap:
        intake_cap = cv2.VideoCapture(1)


# Init pipelines
intake = Intake()

while True:
    init_cap()

    # Run intake pipeline and get data
    ball_detected = False
    ret, intake_frame = intake_cap.read()
    if ret:
        ball_detected = intake.process(intake_frame)
        cv2.imshow("Intake", intake_frame)

        # if intake.red_blob_detector.mask is not None:
            # cv2.imshow("Intake mask", intake.red_blob_detector.mask)
        # if intake.red_blob_detector.canny_frame is not None:
            # cv2.imshow("intake canny", intake.red_blob_detector.canny_frame)

    print((ball_detected))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

intake_cap.release()
cv2.destroyAllWindows()
