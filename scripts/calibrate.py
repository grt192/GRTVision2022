# Credit: 13Ducks on GitHub; modifications for running on Jetson
# calibrate.py should be run on your PC (not the Jetson); use the relevant USB camera and save the outputted matrices

import numpy as np
import cv2
import time

# Calibration termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((6 * 9, 3), np.float32)
objp[:, :2] = np.mgrid[0:9, 0:6].T.reshape(-1, 2)

# Arrays to store object points and image points from all the images.
objpoints = []  # 3d point in real world space
imgpoints = []  # 2d points in image plane.

cap = cv2.VideoCapture(1)

# Print the image resolution for debugging
_, img = cap.read()
h, w, _ = img.shape
print('Resolution: ' + str(w) + ' x ' + str(h))

count = 0

# Begin calibration
while cap.isOpened():
    _, img = cap.read()
    cv2.imshow('orig', img)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Find the chessboard corners
    ret, corners = cv2.findChessboardCorners(gray, (9, 6), None)

    # If found, add object points, image points (after refining them)
    if ret:
        objpoints.append(objp)

        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners2)

        # Draw and display the corners
        img = cv2.drawChessboardCorners(img, (9, 6), corners2, ret)
        cv2.imshow('img', img)

        count += 1
        print(str(count))

        cv2.waitKey(1000)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        print('Stopping calibration...')
        break

ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
print('Printing camera matrices...')
print(mtx)  # Print camera matrix and distortion coefficients
print(dist)

cv2.destroyAllWindows()

_, img = cap.read()
h, w = img.shape[:2]
newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
print('Printing optimal camera matrix')
print(newcameramtx)

# Calculate re-projection error
mean_error = 0
for i in range(len(objpoints)):
    imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs[i], tvecs[i], mtx, dist)
    error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
    mean_error += error
print("Total error: {}".format(mean_error / len(objpoints)))

print('Displaying undistorted image...')
while cap.isOpened():
    _, img = cap.read()
    # Undistort
    dst = cv2.undistort(img, newcameramtx, dist, None, newcameramtx)

    # Crop the image
    x, y, w, h = roi
    dst = dst[y:y + h, x:x + w]
    cv2.imshow('new', dst)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
