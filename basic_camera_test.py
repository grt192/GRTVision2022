import cv2

# Rotate through the 4 USB ports until camera frames are obtained
input_port = 0
num_ports = 4

cap = None
img = None

g_str = ('gst-launch-1.0 -v v4l2src device=/dev/video{} !'
         'jpegdec !'
         'video/x-raw, framerate=(fraction){}/1, width=(int){}, height=(int){} !'
         'videoconvert !'
         'nvoverlaysink')

while img is None:
    time.sleep(1)

    print("Error: No image to process. Cannot run vision pipeline. Are images being captured from the camera?")

    # Try a different port
    input_port = (input_port + 1) % num_ports
    cap = cv2.VideoCapture(g_str.format(input_port, 30, 1920, 1080), cv2.CAP_GSTREAMER)
    _, img = cap.read()
    print("Trying /dev/video" + str(input_port))

# Begin calibration
while cap.isOpened():
    _, img = cap.read()
    cv2.imshow('orig',img)

    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    # Find the chessboard corners
    ret, corners = cv2.findChessboardCorners(gray, (9,6),None)

    # If found, add object points, image points (after refining them)
    if ret:
        objpoints.append(objp)

        corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
        imgpoints.append(corners2)

        # Draw and display the corners
        img = cv2.drawChessboardCorners(img, (9,6), corners2,ret)
        cv2.imshow('img',img)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)
print(mtx, dist)

cv2.destroyAllWindows()

_, img = cap.read()
h,  w = img.shape[:2]
newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))
print(newcameramtx)

while cap.isOpened():
    _, img = cap.read()
    # Undistort
    dst = cv2.undistort(img, newcameramtx, dist, None, newcameramtx)

    # Crop the image
    x,y,w,h = roi
    dst = dst[y:y+h, x:x+w]
    cv2.imshow('new',dst)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()