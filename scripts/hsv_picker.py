'''
Script that allows you to select an image, select a pixel on the image, and calculate the desired HSV low/high range
given a set of tolerances. It also shows you the masked image if that range were to be used.
Modified from https://github.com/alieldinayman/hsv-color-picker/blob/master/HSV%20Color%20Picker.py
'''

import cv2
import numpy as np
import datetime

hue_bound = 180
sat_bound = 255
val_bound = 255

hue_tolerance = 10
sat_tolerance = 10
val_tolerance = 40


# Returns boundaries for a value given +- tolerance, boundaries, and if upper or lower bound
def get_bound(value, tolerance, upper_bound):
    lower_bound = 0  # by default. Upper bound is set by caller

    upper_value = (value + tolerance) if (value + tolerance < upper_bound) else upper_bound
    lower_value = (value - tolerance) if (value - tolerance >= lower_bound) else lower_bound

    # Return the final bound (as a tuple)
    return lower_value, upper_value


def pick_color(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        pixel = image_hsv[y, x]

        # Calculate HSV bounds from pixel
        hue = get_bound(pixel[0], hue_tolerance, hue_bound)
        sat = get_bound(pixel[1], sat_tolerance, sat_bound)
        val = get_bound(pixel[2], val_tolerance, val_bound)

        lower = np.array([hue[0], sat[0], val[0]])
        upper = np.array([hue[1], sat[1], val[1]])

        print(datetime.datetime.now().strftime('%I:%M:%S'), lower, upper)

        # Display masked image
        image_mask = cv2.inRange(image_hsv, lower, upper)
        cv2.imshow("Mask", image_mask)


file_path = '../images_2/image_1.png'
image_src = cv2.imread(file_path)
cv2.imshow("BGR", image_src)

# Convert to HSV
image_hsv = cv2.cvtColor(image_src, cv2.COLOR_BGR2HSV)
cv2.imshow("HSV", image_hsv)

# Triggers color picker when image is clicked
cv2.setMouseCallback("BGR", pick_color)

cv2.waitKey(0)
cv2.destroyAllWindows()