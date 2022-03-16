from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import cv2


def start_http_server(pipeline, frame_source, address, port):
    '''
    Runs the http server. This function should be used as the target for a thread so that the "serve_forever" call
    doesn't stall the main thread.
    @params
    pipeline -- pipeline object as specified by GenericPipeline
    frame_source -- image Source object that contains a function: get_frame() that returns an image or None
    address -- str (ie. 'localhost', '10.1.92.94')
    port -- int
    '''
    def handler(*args):
        GenericCamHandler(pipeline, frame_source, address, port, *args)

    server = ThreadedHTTPServer((address, port), handler)
    print('server started at http://' + address + ':' + str(port) + '/cam.html')
    server.serve_forever()


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


class GenericCamHandler(BaseHTTPRequestHandler):

    def __init__(self, pipeline, frame_source, address, port, *args):
        self.pipeline = pipeline
        self.address = address
        self.port = port
        self.frame_source = frame_source
        self.frame = None  # pre-allocate image to save memory
        BaseHTTPRequestHandler.__init__(self, *args)

    def url(self, path):
        return 'http://' + str(self.address) + ':' + str(self.port) + '/' + path

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

            while True:
                try:
                    # Get the frame and process it
                    print(self.frame_source)
                    self.frame = self.frame_source.get_frame()
                    self.pipeline.process(self.frame)

                    for output_frame in self.pipeline.get_output_frames():
                        # Stream the frame
                        name = output_frame['name']
                        frame = output_frame['frame']

                        if arg == name:
                            img_str = cv2.imencode('.jpg', frame)[1].tobytes()
                            self.send_header('Content-type', 'image/jpeg')
                            self.send_header('Content-length', len(img_str))
                            self.end_headers()
                            self.wfile.write(img_str)
                            self.wfile.write(b"\r\n--jpgboundary\r\n")
                            break


                except KeyboardInterrupt:
                    self.wfile.write(b"\r\n--jpgboundary--\r\n")
                    break
                except BrokenPipeError:
                    continue
            return

        if self.path.endswith('.html'):
            # Overall webpage that serves images and data
            if arg == 'cam':
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write('<html><head></head><body>'.encode('UTF-8'))

                # Write image streams to webpage
                for output_frame in self.pipeline.get_output_frames():
                    self.wfile.write(('<img style="margin-right: 20px;" src="'
                                      + self.url(output_frame['name'] + '.mjpg"') + '/>').encode('UTF-8'))

                # Write vision data to webpage
                self.wfile.write(('<embed type="text/html" src="' + self.url('data.html')
                                  + '" width="500" height="200">').encode('UTF-8'))

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
                        output_str = '<p>('

                        for datum in self.pipeline.get_output_data():
                            output_str += str(datum) + ', '

                        output_str = output_str[:-2]  # remove the last comma & space
                        output_str += ')</p>'

                        # Add data via paragraph
                        self.wfile.write(output_str.encode('UTF-8'))
                        self.wfile.write('</body></html>'.encode('UTF-8'))
                    except BrokenPipeError:
                        continue
                self.wfile.write('</body></html>'.encode('UTF-8'))
