from red_contour_grip import RedContoursPipeline

import config

import cv2
import time
import math

def calculate_coords(frame_width, frame_height, x_cam_coord, y_cam_coord):
    cx = frame_width / 2 - 0.5
    cy = frame_height / 2 - 0.5

    pitch_angle = math.atan(y_cam_coord - cy) / config.focal_len
    yaw_angle = math.atan(x_cam_coord - cx) / config.focal_len

    #print("pitch angle: " + str(pitch_angle))
    #print("yaw angle: " + str(yaw_angle))

    return pitch_angle, yaw_angle

def calc_contours(c):
    M = cv2.moments(c)
    if M['m00'] != 0:
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])

    return cx,cy

input_port = 0
num_ports = 4

cap = cv2.VideoCapture(input_port)
_, frame = cap.read()

# Keep trying until image is obtained
while frame is None:

    print("Error: No image to process. Cannot run vision pipeline. Are images being captured from the camera?")

    # Try a different port
    input_port = (input_port + 1) % num_ports
    cap = cv2.VideoCapture(input_port)

    # Read frame
    _, frame = cap.read()

    print("Trying /dev/video" + str(input_port))

    # Wait before trying the next USB port
    time.sleep(1)

# Put image width and height on table
h, w, _ = frame.shape

# Run the pipeline on the video stream
while True:

    _, frame = cap.read()

    if frame is None:
        continue

    # Undistort the frame
    temp = cv2.undistort(frame, config.cameramtx, config.dist, None, config.newcameramtx)
    # TODO Crop the frame using roi
    frame = temp

    # Process frame
    visionPipeline = RedContoursPipeline() # LemonVisionGripPipeline()
    visionPipeline.process(frame)

    # Retrieve the blobs from the pipeline
    contours = visionPipeline.filter_contours_output # tuple of KeyPoint objects

    print(str(len(contours)) + " blobs detected")

    if len(contours) > 0:
        # Find largest contour
        largest_contour = []
        largest_contour_idx = 0 
        for i in range(len(contours)):
            if (len(contours[i]) > len(largest_contour)):
                largest_contour = contours[i]
                largest_contour_idx = i

        # Find centroid of contour
        x, y = calc_contours(largest_contour)
        x = int(x)
        y = int(y)
        
        cv2.line(frame, (x - config.line_length, y), (x + config.line_length, y), (0, 0, 255), 2)
        cv2.line(frame, (x, y - config.line_length), (x, y + config.line_length), (0, 0, 255), 2)

        temp = cv2.drawContours(frame, contours, largest_contour_idx, (0, 0, 255), 2, cv2.LINE_8, maxLevel=0)
        frame = temp

        # Calculate angle to target
        pitch_angle, yaw_angle = calculate_coords(w, h, x, y)
        
        print("pitch: " + str(pitch_angle) + "; yaw: " + str(yaw_angle))

    cv2.imshow('image', frame)

    if cv2.waitKey(1000) & 0xFF == ord('q'):
        break
