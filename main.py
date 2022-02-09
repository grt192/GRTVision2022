import cv2
import socket
from turret import Turret
import sys

HOST = ''  # Empty string to accept connections on all available IPv4 interfaces
PORT = 30000  # Port to listen on (non-privileged ports are > 1023)

# on Jetson: run python main.py False
is_local = True
if len(sys.argv) > 1:
    is_local = sys.argv[1]

# Function to initialize video captures
stream_res = (160, 120)
fps = 30

turret_cap = None
intake_cap = None


def init_cap(cam=None):
    global is_local

    if cam is None or cam == 'turret':
        global turret_cap
        turret_cap = cv2.VideoCapture(0 if is_local else '/dev/cam/turret')
        turret_cap.set(cv2.CAP_PROP_EXPOSURE, -10)
        
        turret_cap.set(cv2.CAP_PROP_FRAME_WIDTH, stream_res[0])
        turret_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, stream_res[1])
    
    if cam is None or cam == 'intake':
        global turret_cap
        turret_cap = cv2.VideoCapture(1 if is_local else '/dev/cam/intake')
        
        turret_cap.set(cv2.CAP_PROP_FRAME_WIDTH, stream_res[0])
        turret_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, stream_res[1])    


# Initialize video capture
init_cap()

# Init pipelines
turret = Turret()

turret_stream = None

# Init camera servers
if not is_local:
    from cscore import CameraServer, CvSource, VideoMode
    
    cam_server = CameraServer.getInstance()
    cam_server.enableLogging()

    # Create camera server for turret
    print('Attempting add a MjpegServer for turret')
    turret_server = cam_server.addServer(name='Turret')
    print('Completed attempt to add server for turret')
    turret_stream = CvSource('Turret', VideoMode.PixelFormat.kMJPEG, stream_res[0], stream_res[1], fps)
    turret_server.setSource(turret_stream)
    print('CvSource has been set for Turret at port ' + str(turret_server.getPort()))


# Loop to connect to socket
while True:
    try:
        print('Attempting to connect')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)
            
            # Loop to run everything
            while True:
                # Init video captures if not already
                while not (turret_cap.isOpened() and intake_cap.isOpened()):
                    if not turret_cap.isOpened():
                        print('Error opening turret capture... retrying')
                        init_cap('turret')
                    if not intake_cap.isOpened(): 
                        print('Error opening intake capture... retrying')
                        init_cap('intake')
                
                # Run turret pipeline
                ret, turret_frame = turret_cap.read()
                if ret:
                    turret_frame, data = turret.process(turret_frame)

                    # If Jetson: send data and put frame
                    if not is_local:
                        conn.send(bytes(str(data) + "\n", "UTF-8"))
                        turret_stream.putFrame(turret_frame)
                    # If local: show frame
                    else:
                        cv2.imshow('Turret', turret_frame)

                # Exit?
                if is_local & cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
    except (BrokenPipeError, ConnectionResetError, ConnectionRefusedError) as e:
        print("Connection lost... retrying")
    
cv2.destroyAllWindows()
