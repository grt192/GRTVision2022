import cv2
import math

import config

def calculate_angles(frame_width, frame_height, u, v):

    #yaw_angle = math.degrees(math.atan((u - config.cx) / config.focal_x))
    #pitch_angle = -math.degrees(math.atan((v - config.cy) / config.focal_y))
    
    yaw_angle = math.degrees(math.atan((u - (frame_width/2 - 0.5)) / config.focal_x))
    pitch_angle = -math.degrees(math.atan((v - (frame_height/2 - 0.5)) / config.focal_y))

    return pitch_angle, yaw_angle

def calculate_centroid(c):
    M = cv2.moments(c)
    if M['m00'] != 0:
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])

    return cx, cy

def draw_center_point(frame, x, y):
    cv2.line(frame, (x - config.center_line_length, y), (x + config.center_line_length, y), config.color, config.line_thickness)
    cv2.line(frame, (x, y - config.center_line_length), (x, y + config.center_line_length), config.color, config.line_thickness)

def draw_text(frame, x, y, text):
    temp = cv2.putText(frame, text, (x + config.text_offset, y - config.text_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, config.color, config.line_thickness)
    frame = temp