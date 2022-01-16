import numpy as np

# [ [fx, 0, cx], [0, fy, cy], [0, 0, 1] ]
cameramtx = np.array([[662.3461673, 0, 293.51663222], [0, 664.22509824, 243.65759666],[  0, 0, 1]] )
dist = np.array([[2.47936730e-01, -2.34092515e+00, 2.73073943e-03, -1.58373364e-03, 7.08333922e+00]])

newcameramtx = np.array([[675.30944824, 0, 295.30676157], [0, 668.10913086, 243.85860464], [0, 0, 1]])
roi = [] # TODO

focal_x = newcameramtx[0][0]
focal_y = newcameramtx[1][1]

cx = newcameramtx[0][2]
cy = newcameramtx[1][2] 

# Constants for drawing on image
line_thickness = 1
center_line_length = 3
text_offset = 5
color = (255, 255, 255)