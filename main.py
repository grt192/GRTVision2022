
import cv2
import socket
import time
from turret import Turret
from intake import Intake

HOST = ''  # Empty string to accept connections on all available IPv4 interfaces
PORT = 5800  # Port to listen on (non-privileged ports are > 1023)


# Function to initialize video captures
stream_res = (160, 120)
fps = 30

turret_cap = None
intake_cap = None


def init_cap():
    global turret_cap
    global intake_cap

    is_turret_cap = turret_cap is not None and turret_cap.isOpened()
    is_intake_cap = intake_cap is not None and intake_cap.isOpened()

    if not is_turret_cap:
        turret_cap = cv2.VideoCapture('/dev/cam/turret', cv2.CAP_V4L)
        turret_cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 3)
        turret_cap.set(cv2.CAP_PROP_EXPOSURE, -10)
        
        turret_cap.set(cv2.CAP_PROP_FRAME_WIDTH, stream_res[0])
        turret_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, stream_res[1])

    if not is_intake_cap:
        intake_cap = cv2.VideoCapture('/dev/cam/intake', cv2.CAP_V4L)

        intake_cap.set(cv2.CAP_PROP_FRAME_WIDTH, stream_res[0])
        intake_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, stream_res[1])


# Init pipelines
turret = Turret()
intake = Intake()

turret_stream = None
intake_stream = None

# Init camera servers
from cscore import CameraServer, CvSource, VideoMode

cam_server = CameraServer.getInstance()
cam_server.enableLogging()

# Create camera server for turret
turret_server = cam_server.addServer(name='Turret')
turret_stream = CvSource('Turret', VideoMode.PixelFormat.kMJPEG, stream_res[0], stream_res[1], fps)
turret_server.setSource(turret_stream)
print('Server created for Turret at port ' + str(turret_server.getPort()))

# Create camera server for intake
intake_server = cam_server.addServer(name='Intake')
intake_stream = CvSource('Turret', VideoMode.PixelFormat.kMJPEG, stream_res[0], stream_res[1], fps)
intake_server.setSource(intake_stream)
print('Server created for Intake at port ' + str(intake_server.getPort()))


# Loop to connect to socket
while True:
    try:
        print('Attempting to connect')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # https://stackoverflow.com/questions/29217502/socket-error-address-already-in-use
            s.bind((HOST, PORT))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)

                # Loop to run everything
                while True:
                    init_cap()

                    # Run turret pipeline
                    ret, turret_frame = turret_cap.read()
                    turret_vision_status = False
                    turret_theta = 0
                    hub_distance = 0

                    if ret:
                        # Do this out here instead of in turret.py so that the frame gets preserved
                        turret_frame = cv2.rotate(turret_frame, cv2.ROTATE_90_CLOCKWISE)
                        turret_vision_status, turret_theta, hub_distance = turret.process(turret_frame)
                        turret_stream.putFrame(turret_frame)

                    # Run intake pipeline
                    ret, intake_frame = intake_cap.read()
                    ball_detected = False

                    if ret:
                        ball_detected = intake.process(intake_frame)
                        intake_stream.putFrame(intake_frame)

                    # Send data
                    conn.send(bytes(str((turret_vision_status, turret_theta, hub_distance, ball_detected)) + "\n", "UTF-8"))

    except (BrokenPipeError, ConnectionResetError, ConnectionRefusedError) as e:
        print("Connection lost... retrying")