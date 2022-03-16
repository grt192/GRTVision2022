#!/usr/bin/env python3

import cv2
import socket
from Turret import Turret
from intake import Intake
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn


# Init pipelines
turret = Turret()

# Constants
turret_address = 'localhost'
turret_port = 8081


# Start intake and turret camera servers
def start_turret_stream():
    print('starting turret stream THREAD')
    server = ThreadedHTTPServer((turret_address, turret_port), TurretCamHandler)
    print('server started at http://' + turret_address + ':' + str(turret_port) + '/cam.html')
    server.serve_forever()

    while True:
        try:
            pass
        except KeyboardInterrupt:
            server.socket.close()

turret_vision_status = False
turret_theta = 0
hub_distance = 0


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


class TurretCamHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        global turret_vision_status, turret_theta, hub_distance

        # If getting a camera frame
        if self.path.endswith('.mjpg'):
            self.send_response(200)
            self.send_header(
                'Content-type',
                'multipart/x-mixed-replace; boundary=--jpgboundary'
            )
            self.end_headers()

            # Split up HTTP URL to get camera requested
            path_args = self.path.split('/')
            arg = path_args[len(path_args) - 1]  # eg. "cam" of cam.mjpg
            arg = arg[0:(len(path_args) - 7)]

            while True:
                try:

                    # Run turret pipeline
                    turret_frame = cv2.imread(cv2.samples.findFile("images/83.5_9.0.png"))

                    if turret_frame is None:
                        turret_vision_status = False
                        turret_theta = 0
                        hub_distance = 0
                        continue

                    # Do this out here instead of in Turret.py so that the frame gets preserved
                    turret_vision_status, turret_theta, hub_distance = turret.process(turret_frame)
                    print((turret_vision_status, turret_theta, hub_distance))

                    if arg == 'cam':
                        img_str = cv2.imencode('.jpg', turret.output_frame)[1].tobytes()
                        self.send_header('Content-type', 'image/jpeg')
                        self.send_header('Content-length', len(img_str))
                        self.end_headers()
                        self.wfile.write(img_str)

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
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('<html><head></head><body>'.encode('UTF-8'))
            self.wfile.write(('<img style="margin-right: 20px;" src="http://' + turret_address + ':' + str(
                turret_port) + '/cam.mjpg"/>').encode('UTF-8'))
            self.wfile.write(
                ('<img src="http://' + turret_address + ':' + str(turret_port) + '/cam2.mjpg"/>').encode('UTF-8'))

            # Add data via paragraph
            self.wfile.write(('<p>Status: ' + str(turret_vision_status) + '</p>').encode('UTF-8'))
            self.wfile.write(('<p>Turret theta: ' + str(turret_theta) + '</p>').encode('UTF-8'))
            self.wfile.write(('<p>Hub dist: ' + str(hub_distance) + '</p>').encode('UTF-8'))

            self.wfile.write('</body></html>'.encode('UTF-8'))
            return



# Loop to connect to socket
# Start threads for streams
turret_thread = threading.Thread(target=start_turret_stream)
turret_thread.start()

