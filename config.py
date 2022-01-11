import numpy as np

cameramtx = np.array([[662.3461673, 0, 293.51663222], [0, 664.22509824, 243.65759666],[  0, 0, 1]] )
dist = np.array([[2.47936730e-01, -2.34092515e+00, 2.73073943e-03, -1.58373364e-03, 7.08333922e+00]])

newcameramtx = np.array([[675.30944824, 0, 295.30676157], [0, 668.10913086, 243.85860464], [0, 0, 1]])
roi = [] # TODO

focal_len = 500.561894 # in pixels; fy and fx might be different values

nt_ip = '10.1.92.2'

nt_name = 'jetson'

line_length = 10