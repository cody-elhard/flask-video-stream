# This file is just used to log stuff
import sys
import cv2
sys.path.append('image_processing')
from marker import process_image

image = cv2.imread("images/markers.jpg")
processed_image = process_image(image, hardcoded_image = False, should_return_image = True)

cv2.imshow("Processed Image", processed_image)

cv2.waitKey(0)
cv2.destroyAllWindows()

