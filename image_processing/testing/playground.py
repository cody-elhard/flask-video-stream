# This file is just used to log stuff
import sys
import cv2
sys.path.append('image_processing')
from marker import process_image

image = cv2.imread("images/markers.jpg")
process_image(image)

# actual_levels = [.5, .4, .8]
