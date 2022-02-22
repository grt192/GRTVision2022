
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
    hsv = cv2.cvtColor(bilateral_filtered_image, cv2.COLOR_BGR2HSV)



    #low_red = cv2.inRange(hsv, (0, 87, 0), (170, 87, 0))
    high_red = cv2.inRange(hsv, (0, 130, 255), (180, 255, 255))
    blue = cv2.inRange(hsv, (99, 71, 78), (123, 255, 255))

    mask = cv2.bitwise_or(blue, high_red)
    cv2.circle(frame, cam_center, 2, (0, 255, 0), -1)

    #cv2.imshow('Bilateral', bilateral_filtered_image)
    #cv2.imshow('detected circles', frame)
    #cv2.imshow('Edges', edge_detected_image)
    # cv2.imshow('Original', frame)
    # cv2.imshow('Low_red', low_red)
    # cv2.imshow('High_red', high_red)
    # cv2.imshow('Blue', blue)
    cv2.imshow('Bilateral', bilateral_filtered_image)
    cv2.imshow("Mask", mask)


    key = cv2.waitKey(1)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()







