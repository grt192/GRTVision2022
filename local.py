import cv2
from turret import Turret
from intake import Intake


turret_cap = None
intake_cap = None


def init_cap():
    global turret_cap
    global intake_cap

    is_turret_cap = turret_cap is not None and turret_cap.isOpened()
    is_intake_cap = intake_cap is not None and intake_cap.isOpened()

    if not is_turret_cap:
        # turret_cap = cv2.VideoCapture(0) #, cv2.CAP_DSHOW)
        # turret_cap.set(cv2.CAP_PROP_EXPOSURE, -10)
        print('l')

    if not is_intake_cap:
        # print('l')
        intake_cap = cv2.VideoCapture(1) #, cv2.CAP_DSHOW)


# Init pipelines
turret = Turret()
intake = Intake()

while True:
    init_cap()

    # Run turret pipeline
    turret_vision_status = False
    turret_theta = 0
    hub_distance = 0
    '''
    ret, turret_frame = turret_cap.read()
    if ret:
        turret_vision_status, turret_theta, hub_distance = turret.process(turret_frame)
        cv2.imshow("Turret", turret_frame)
    '''

    # Run intake pipeline and get data
    ball_detected = False
    ret, intake_frame = intake_cap.read()
    if ret:
        cv2.imshow("Intake", intake_frame)

        ball_detected = intake.process(intake_frame)
        # if intake.red_blob_detector.mask is not None:
            # cv2.imshow("Intake mask", intake.red_blob_detector.mask)
        # if intake.red_blob_detector.canny_frame is not None:
            # cv2.imshow("intake canny", intake.red_blob_detector.canny_frame)

    print((turret_vision_status, turret_theta, hub_distance, ball_detected))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

turret_cap.release()
intake_cap.release()
cv2.destroyAllWindows()
