import math
import imutils
import config
import numpy as np
import cv2
import glob

import cv2
import numpy as np

# Load image

cap = cv2.VideoCapture(0)
#cap.set(cv2.CAP_PROP_EXPOSURE,-13)

conts = []

while True:

    ret, frame = cap.read()
    num_balls = 0
    h, w, _ = frame.shape
    cam_x = int((w / 2) - 0.5)
    cam_y = int((h / 2) - 0.5)
    cam_center = (cam_x, cam_y)

    img = frame.copy()
    blur = cv2.blur(img, (4, 4))
    bilateral_filtered_image = cv2.bilateralFilter(blur, 5, 175, 175)
    gray = cv2.cvtColor(bilateral_filtered_image, cv2.COLOR_BGR2GRAY)
    #edge_detected_image = cv2.Canny(bilateral_filtered_image, 75, 200)

    # find all  contours in mask
    try:
        #TODO: test and get more accurate parameter values
        circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 20,
                                  param1=50, param2=30, minRadius=230, maxRadius=250)
        circles = np.uint16(np.around(circles))

        for i in circles[0, :]:
            num_balls += 1
            # draw the outer circle
            cv2.circle(frame, (i[0], i[1]), i[2], (0, 255, 0), 2)
            # draw the center of the circle
            cv2.circle(frame, (i[0], i[1]), 2, (0, 0, 255), 3)

    except:
        print("no circles detected")

    cv2.circle(frame, cam_center, 2, (0, 255, 0), -1)
    print("# of balls detected: " + str(num_balls))

    #cv2.imshow('Bilateral', bilateral_filtered_image)
    #cv2.imshow('detected circles', frame)
    #cv2.imshow('Edges', edge_detected_image)
    cv2.imshow('Original', frame)

    key = cv2.waitKey(1)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()
