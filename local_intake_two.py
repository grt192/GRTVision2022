
import cv2
import numpy as np
import imutils

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

    B, G, R = cv2.split(frame)
    M = np.maximum(np.maximum(R, G), B)

    # R[R < M] = 0
    # #G[G < M] = 0
    # B[B < M] = 0

    # R[R < M] = 400
    G[G < M] = 0
    # B[B < M] = 400

    output = cv2.merge((B, G, R))
    h, w, _ = frame.shape
    num_balls = 0
    cam_x = int((w / 2) - 0.5)
    cam_y = int((h / 2) - 0.5)
    cam_center = (cam_x, cam_y)

    img = output.copy()
    blur = cv2.blur(img, (4, 4))
    bilat = cv2.bilateralFilter(blur, 5, 175, 175)
    e = cv2.erode(blur, None, iterations=1)
    d = cv2.dilate(e, None, iterations=1)
    # mask_red = cv2.inRange(d, (0, 130, 255), (180, 255, 255))
    # mask_blue = cv2.inRange(d, (99, 71, 78), (123, 255, 255))
    hsv = cv2.cvtColor(d, cv2.COLOR_BGR2HSV)
    mask_red = cv2.inRange(hsv, (0, 130, 255), (200, 255, 255))
    mask_blue = cv2.inRange(hsv, (120, 100, 0), (140, 255, 255))
    mask_comp = cv2.bitwise_or(mask_red, mask_blue)

    try:
        contours = cv2.findContours(mask_comp.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)
        print("yeah")

        output = []

        if len(contours) != 0:
            print("contours")
            for c in contours:
                x, y, w, h = cv2.boundingRect(c)
                aspect_ratio = float(w / h)
                approx = cv2.approxPolyDP(c, 0.01 * cv2.arcLength(c, True), True)
                area = cv2.contourArea(c)
                # if .75 < aspect_ratio < 1.25:
                # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 1)
                if (30 < area < 100 ):
                    M = cv2.moments(c)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])  # (testing)
                        cy = int(M["m01"] / M["m00"])
                    else:
                        cx, cy = 0, 0
                    center = [cx, cy]
                    output.append([x, y, w, h])

                for o in output:
                    o[0] = x
                    o[1] = y
                    o[2] = w
                    o[3] = h
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 7)

    except:
        print("no circles detected")

    cv2.circle(frame, cam_center, 2, (0, 255, 0), -1)
    print("# of balls detected: " + str(num_balls))

    # cv2.imshow('Bilateral', bilateral_filtered_image)
    # cv2.imshow('detected circles', frame)
    # cv2.imshow('Edges', edge_detected_image)
    cv2.imshow('Original', frame)
    # cv2.imshow('gray', gray)
    # cv2.imshow("rgb", rgb)
    #cv2.imshow("output", mask_comp)

    key = cv2.waitKey(1)
    if key == 27:
        break

cap.release()
cv2.destroyAllWindows()







