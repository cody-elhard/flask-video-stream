# This file is just used to log stuff
import sys
import cv2
sys.path.append('image_processing/experimental')
from marker_returns_array import process_image

image = cv2.imread("images/markers.jpg")
process_image(image)

# actual_levels = [.5, .4, .8]
