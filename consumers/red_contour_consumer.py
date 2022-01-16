import cv2
import numpy as np
import util.helper

from consumers.consumer_interface import ConsumerInterface


class RedContourConsumer(ConsumerInterface):
    def __init__(self, name='0'):
        self.stream = None
        self.name = name

        self.blur_radius = 3
        
        self.hsv_hue = [0.0, 11.058020477815704]
        self.hsv_sat = [100, 255.0]
        self.hsv_val = [150, 255.0]
        self.contour_min_area = 1000.0
        self.contour_max_vertices = 1000000.0
        self.contour_min_vertices = 0
        self.contour_min_ratio = 0
        self.contour_max_ratio = 1000

    def process_frame(self, frame):
        if self.stream is None:
            self.stream = np.copy(frame)
        else:
            np.copyto(self.stream, frame)

        # Blur
        ksize = int(6 * round(self.blur_radius) + 1)
        temp = cv2.GaussianBlur(self.stream, (ksize, ksize), round(self.blur_radius))

        # HSV threshold
        temp = cv2.cvtColor(temp, cv2.COLOR_BGR2HSV)
        temp = cv2.inRange(temp, (self.hsv_hue[0], self.hsv_sat[0], self.hsv_val[0]), (self.hsv_hue[1], self.hsv_sat[1], self.hsv_val[1]))

        # Find contours
        contours, hierarchy = cv2.findContours(temp, mode=cv2.RETR_LIST, method=cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours
        filtered_contours = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            area = cv2.contourArea(contour)
            if (area < self.contour_min_area):
                continue
            if (len(contour) < self.contour_max_vertices or len(contour) > self.contour_max_vertices):
                continue
            ratio = (float)(w) / h
            if (ratio < self.contour_min_ratio or ratio > self.contour_max_ratio):
                continue
            filtered_contours.append(contour)

        # Find largest contour
        largest_contour = []
        largest_contour_idx = 0
        for i in range(len(contours)):
            if (len(contours[i]) > len(largest_contour)):
                largest_contour = contours[i]
                largest_contour_idx = i
    
        if len(largest_contour) > 0:
            x, y = util.helper.calculate_centroid(largest_contour)

            util.helper.draw_center_point(self.stream, x, y)
            util.helper.draw_contour(self.stream, largest_contour, largest_contour_idx)

        return (self.stream, {'test': 'test!'})

    def get_name(self):
        return self.name
