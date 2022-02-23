import numpy as np

new_image_points = np.zeros((4, 2), np.float32)
image_points = np.array([[0, 0],
                         [0, 0],
                         [0, 0],
                         [0, 0]])
for i in range(3):
    mid_x = (image_points[i][0] + image_points[i + 1][0]) / 2
    mid_y = (image_points[i][1] + image_points[i + 1][1]) / 2
    new_image_points[i, 0] = mid_x
    new_image_points[i, 1] = mid_y
