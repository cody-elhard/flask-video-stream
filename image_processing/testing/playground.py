# This file is just used to log stuff
import sys
import cv2
sys.path.append('image_processing')
from marker import process_image

image = cv2.imread("images/markers.jpg")
water_levels = process_image(image)

actual_levels = [.5, .8, .4]

threshold = 0.2

for i, actual_level in enumerate(actual_levels):
  assert actual_level + threshold > water_levels[i] > actual_level - threshold