import cv2
from turret import Turret


turret_cap = None
intake_cap = None


def init_cap():
    global turret_cap
    global intake_cap

    is_turret_cap = turret_cap is not None and turret_cap.isOpened()
    is_intake_cap = intake_cap is not None and intake_cap.isOpened()

    if not is_turret_cap:
        turret_cap = cv2.VideoCapture(0)
        turret_cap.set(cv2.CAP_PROP_EXPOSURE, -10)

    if not is_intake_cap:
        # TODO init intake capture
        print('todo')


# Init pipelines
turret = Turret()

while True:
    init_cap()

    # Run turret pipeline
    ret, turret_frame = turret_cap.read()
    if ret:
        turret_vision_status, turret_theta, hub_distance = turret.process(turret_frame)
        cv2.imshow("Turret", turret_frame)
    else:
        turret_vision_status = False
        turret_theta = 0
        hub_distance = 0

    # TODO Run intake pipeline and get data
    ball_detected = False

    print((turret_vision_status, turret_theta, hub_distance, ball_detected))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
