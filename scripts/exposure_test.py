import cv2
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

cap = None
img = None
stream_res = (160, 120)

def init_cap():
    global cap

    is_cap = cap is not None and cap.isOpened()

    if not is_cap:
        print('turret cap not initialized, trying again')
        cap = cv2.VideoCapture('/dev/cam/turret', cv2.CAP_V4L)
        cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
        cap.set(cv2.CAP_PROP_EXPOSURE, 10)

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, stream_res[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, stream_res[1])


address = '10.1.92.94'
port = 5800

class CamHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        global cap, img

        if self.path.endswith('.mjpg'):
            self.send_response(200)
            self.send_header(
                'Content-type',
                'multipart/x-mixed-replace; boundary=--jpgboundary'
            )
            self.end_headers()
            while True:
                try:
                    init_cap()

                    rc, img = cap.read()
                    if not rc:
                        init_cap()
                        continue

                    img_str = cv2.imencode('.jpg', img)[1].tobytes()

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
            self.wfile.write(('<img src="http://' + address + ':' + str(port) + '/cam.mjpg"/>').encode('UTF-8'))
            self.wfile.write('</body></html>'.encode('UTF-8'))
            return


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


def main():

    try:
        server = ThreadedHTTPServer((address, port), CamHandler)
        print('server started at http://' + address + ':' + str(port) + '/cam.html')
        server.serve_forever()
    except KeyboardInterrupt:
        cap.release()
        server.socket.close()


if __name__ == '__main__':
    main()
