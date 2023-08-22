import numpy as np
import cv2

def calc_landmark_list(image, hand):
    image_width = image.shape[0]
    image_height = image.shape[1]

    landmark_point = []

    for _, landmark in enumerate(hand.landmark):
        landmark_x = min(int(landmark.x * image_width), image_width - 1)
        landmark_y = min(int(landmark.y * image_height), image_height - 1)
        landmark_point.append([landmark_x, landmark_y])
        
    return landmark_point