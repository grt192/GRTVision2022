#!/usr/bin/env python3

from Turret import Turret
from Intake import Intake
import threading
import socket
import time

from GenericHTTPServer import start_http_server
from TurretSource import TurretSource
from IntakeSource import IntakeSource
from StaticImageSource import StaticImageSource


class Main:

    def __init__(self, jetson, connect_socket, turret_source=None, intake_source=None):
        '''
        jetson (bool): True if running on Jetson, False otherwise.
            This controls the address and port #s, as well as the image sources for turret and intake
            (ie. dev/cam/turret vs 0)

        connect_socket (bool): True if you want to run the data socket connection. Will connect via 1337 localhost or
            5800

        turret_source (image source object): Leave None if you want the video capture to be the image source for the
            vision pipeline. Options: None or StaticImageSource obj

        intake_source: same as turret_source but for intake duh
        '''

        print('Entered Main')
        # Initialize vision pipelines
        self.turret = Turret()
        self.intake = Intake()

        if jetson:
            address = '10.1.92.94'
            ports = (5801, 5802)
        else:
            address = 'localhost'
            ports = (8081, 8082)

        self.connect_socket = connect_socket
        self.jetson = jetson

        # Start threads
        print('Starting threads...')
        turret_thread = threading.Thread(target=start_http_server, args=(self.turret, (TurretSource(jetson) if turret_source is None else turret_source), address, ports[0]))
        intake_thread = threading.Thread(target=start_http_server, args=(self.intake, (IntakeSource(jetson) if intake_source is None else intake_source), address, ports[1]))
        turret_thread.start()
        intake_thread.start()

        # Run the main code
        self.run()

    # Just run once! Infinite loop that keeps the streaming threads alive whilst sending socket data (if applicable)
    def run(self):
        if self.connect_socket:
            if self.jetson:
                HOST = ''
                PORT = 5800
            else:
                HOST = ''  # Empty string to accept connections on all available IPv4 interfaces
                PORT = 1337  # Port to listen on (non-privileged ports are > 1023)

            # Connect to socket
            while True:
                try:
                    print('Attempting to connect')

                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.bind((HOST, PORT))
                        s.listen()
                        conn, addr = s.accept()
                        with conn:
                            print('Connected by', addr)

                            # Send data over socket connection
                            while True:
                                output_data = self.turret.get_output_values() + self.intake.get_output_values()
                                print('send data', str(output_data))
                                conn.send(bytes(str(output_data) + "\n", "UTF-8"))
                                time.sleep(0.1)
                            break

                except (BrokenPipeError, ConnectionResetError, ConnectionRefusedError) as e:
                    print('Connection lost... retrying')
                except KeyboardInterrupt as e:
                    break
        else:
            while True:
                pass


if __name__ == '__main__':
    # Main(jetson=False, connect_socket=False)
    Main(jetson=False, connect_socket=True, turret_source=StaticImageSource('images/129.75_6.0.png'), intake_source=StaticImageSource('images/129.75_6.0.png'))
