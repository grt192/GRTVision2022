#!/usr/bin/env python3

import cv2
import socket
import math
import time
from turret import Turret
from intake import Intake
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn


# Constants
HOST = ''  # Empty string to accept connections on all available IPv4 interfaces
PORT = 5800  # Port to listen on (non-privileged ports are > 1023)

stream_res = (160, 120)
fps = 30

turret_address = 'localhost'
turret_port = 8081
intake_address = 'localhost'
intake_port = 8082
'''
turret_address = '10.1.92.94'
turret_port = 5801
intake_address = '10.1.92.94'
intake_port = 5802
'''
# Init pipelines
turret = Turret()
intake = Intake()

# Global variables
turret_server = None
intake_server = None
turret_frame = None
intake_frame = None
turret_cap = None
intake_cap = None

# Vision data to send
turret_vision_status = False
turret_theta = 0
hub_distance = 0
ball_detected = False


def init_turret_cap():
    global turret_cap

    is_turret_cap = turret_cap is not None and turret_cap.isOpened()

    if not is_turret_cap:
        print('turret cap not initialized, trying again')
        turret_cap = cv2.VideoCapture('/dev/cam/turret', cv2.CAP_V4L)
        turret_cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
        turret_cap.set(cv2.CAP_PROP_EXPOSURE, 10)  # 5 to 2000

        # Use default resolution to match calibrated camera matrix
        # turret_cap.set(cv2.CAP_PROP_FRAME_WIDTH, stream_res[0])
        # turret_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, stream_res[1])


def init_intake_cap():
    global intake_cap

    is_intake_cap = intake_cap is not None and intake_cap.isOpened()

    if not is_intake_cap:
        print('intake cap not initialized, trying again')
        intake_cap = cv2.VideoCapture('/dev/cam/intake', cv2.CAP_V4L)

        intake_cap.set(cv2.CAP_PROP_FRAME_WIDTH, stream_res[0])
        intake_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, stream_res[1])


# Functions to start turret and intake stream threads
def start_turret_stream():
    global turret_server

    print('starting turret stream THREAD')
    turret_server = ThreadedHTTPServer((turret_address, turret_port), TurretCamHandler)
    print('server started at http://' + turret_address + ':' + str(turret_port) + '/cam.html')
    turret_server.serve_forever()  # Runs forever


def start_intake_stream():
    global intake_server

    print('starting intake stream THREAD')
    intake_server = ThreadedHTTPServer((intake_address, intake_port), IntakeCamHandler)
    print('server started at http://' + intake_address + ':' + str(intake_port) + '/cam.html')
    intake_server.serve_forever()  # Runs forever


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


class TurretCamHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        # Split up HTTP URL so we know which page was requested
        path_args = self.path.split('/')
        arg = path_args[len(path_args) - 1]  # eg. "cam" of cam.mjpg
        arg = arg[0:(len(path_args) - 7)]

        # If getting a camera frame
        if self.path.endswith('.mjpg'):
            self.send_response(200)
            self.send_header(
                'Content-type',
                'multipart/x-mixed-replace; boundary=--jpgboundary'
            )
            self.end_headers()

            # Declare global here so we can edit the value of the variable later
            global turret_cap, turret_frame
            global turret_vision_status, turret_theta, hub_distance

            while True:
                try:
                    # init_turret_cap()

                    # Run turret pipeline
                    # ret, turret_frame = turret_cap.read()

                    turret_frame = cv2.imread("./images/test_187.png")
                    # test_120 produces 106'' distance calc --> 14'' off
                    # test_187 produces 146'' distance calc --> 21'' off
                    # if not ret:
                    if turret_frame is None:
                        turret_vision_status = False
                        turret_theta = 0
                        hub_distance = 0
                        continue

                    turret_vision_status, turret_theta, hub_distance = turret.process(turret_frame)
                    # Rotate the turret frame (for display)
                    # Do this out here instead of in turret.py so that the frame gets preserved
                    # Commented out to fix weird flickering issues
                    # turret_frame = cv2.rotate(turret_frame, cv2.ROTATE_90_CLOCKWISE)


                    # OG image stream
                    if arg == 'cam':
                        img_str = cv2.imencode('.jpg', turret.output_frame)[1].tobytes()
                        self.send_header('Content-type', 'image/jpeg')
                        self.send_header('Content-length', len(img_str))
                        self.end_headers()
                        self.wfile.write(img_str)

                    # 2nd image stream (helps with debugging)
                    elif arg == 'cam2':
                        mask_img_str = cv2.imencode('.jpg', turret.masked_output)[1].tobytes()
                        self.send_header('Content-type', 'image/jpeg')
                        self.send_header('Content-length', len(mask_img_str))
                        self.end_headers()
                        self.wfile.write(mask_img_str)

                    self.wfile.write(b"\r\n--jpgboundary\r\n")

                except KeyboardInterrupt:
                    self.wfile.write(b"\r\n--jpgboundary--\r\n")
                    break
                except BrokenPipeError:
                    continue
            return

        if self.path.endswith('.html'):
            # Overall webpage that serves: images and data
            if arg == 'cam':
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write('<html><head></head><body>'.encode('UTF-8'))
                self.wfile.write(('<img style="margin-right: 20px;" src="http://' + turret_address + ':' + str(turret_port)
                                  + '/cam.mjpg"/>').encode('UTF-8'))
                self.wfile.write(('<img src="http://' + turret_address + ':' + str(turret_port) + '/cam2.mjpg"/>')
                                 .encode('UTF-8'))

                if turret_frame is not None:
                    h, w, _ = turret_frame.shape
                    self.wfile.write(('<p>Resolution: ' + str(w) + 'x' + str(h) + '</p>')
                                     .encode('UTF-8'))
                self.wfile.write(('<embed type="text/html" src="http://' + turret_address + ':' + str(turret_port)
                                  + '/data.html" width="500" height="200">').encode('UTF-8'))

                self.wfile.write('</body></html>'.encode('UTF-8'))
                return
            # Webpage that serves the vision data
            elif arg == 'data':
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write('<html><head></head><body>'.encode('UTF-8'))
                # Keep writing and updating the webpage
                # TODO it creates a giant list but doesn't scroll at all
                while True:
                    try:
                        # Add data via paragraph (can directly access global data vars w/o global declaration)
                        self.wfile.write(('<p>(' + str(turret_vision_status) + ', ' + str(turret_theta) + ' deg, ' + str(hub_distance) + ')</p>').encode('UTF-8'))
                        self.wfile.write('</body></html>'.encode('UTF-8'))
                    except BrokenPipeError:
                        continue
                self.wfile.write('</body></html>'.encode('UTF-8'))


class IntakeCamHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path.endswith('.mjpg'):
            self.send_response(200)
            self.send_header(
                'Content-type',
                'multipart/x-mixed-replace; boundary=--jpgboundary'
            )
            self.end_headers()

            global ball_detected
            global intake_frame

            while True:
                try:
                    init_intake_cap()

                    # Run intake pipeline
                    ret, intake_frame = intake_cap.read()

                    if not ret:
                        ball_detected = False
                        continue

                    ball_detected = intake.process(intake_frame)

                    img_str = cv2.imencode('.jpg', intake_frame)[1].tobytes()

                    self.send_header('Content-type', 'image/jpeg')
                    self.send_header('Content-length', len(img_str))
                    self.end_headers()

                    self.wfile.write(img_str)
                    self.wfile.write(b"\r\n--jpgboundary\r\n")

                except KeyboardInterrupt:
                    self.wfile.write(b"\r\n--jpgboundary--\r\n")
                    break
                except BrokenPipeError:
                    continue
            return

        if self.path.endswith('.html'):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('<html><head></head><body>'.encode('UTF-8'))
            self.wfile.write(('<img src="http://' + intake_address + ':' + str(intake_port) + '/cam.mjpg"/>').encode('UTF-8'))
            # TODO (fix this, it doesn't actually update properly). Use red/green circle in the corner of frame instead
            # self.wfile.write(('<p>Balls? ' + str(ball_detected) + '</p>').encode('UTF-8'))
            self.wfile.write('</body></html>'.encode('UTF-8'))
            return


# Loop to connect to socket
# Loop to run everything
'''
while True:
    try:
        print('Attempting to connect')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)

                # Start threads for streams
                turret_thread = threading.Thread(target=start_turret_stream)
                turret_thread.start()

                intake_thread = threading.Thread(target=start_intake_stream)
                intake_thread.start()

                while True:
                    try:
                        # Send data
                        conn.send(bytes(str((turret_vision_status, turret_theta, hub_distance, ball_detected)) + "\n", "UTF-8"))
                        # print((turret_vision_status, turret_theta, hub_distance, ball_detected))
                        pass
                    except KeyboardInterrupt as e:
                        turret_server.socket.close()
                        turret_server.shutdown()
                        intake_server.socket.close()
                        intake_server.shutdown()
                        print('KeyboardInterrupt detected in main... terminating')
                        break
    except (BrokenPipeError, ConnectionResetError, ConnectionRefusedError) as e:
        print('Connection lost... retrying')

'''

# Start threads for streams
turret_thread = threading.Thread(target=start_turret_stream)
turret_thread.start()

intake_thread = threading.Thread(target=start_intake_stream)
intake_thread.start()

while True:
    try:
        # Send data
        # conn.send(bytes(str((turret_vision_status, turret_theta, hub_distance, ball_detected)) + "\n", "UTF-8"))
        # print((turret_vision_status, turret_theta, hub_distance, ball_detected))
        pass
    except KeyboardInterrupt as e:
        turret_server.socket.close()
        turret_server.shutdown()
        intake_server.socket.close()
        intake_server.shutdown()
        print('KeyboardInterrupt detected in main... terminating')
        break