import cv2
from image_processing.marker import process_image

def capture_and_save(img, should_return_image = False):
  processed_image = process_image(img, hardcoded_image=True, should_return_image=True)
  cv2.imwrite("images/last.png", resized_image(processed_image, scale=0.5))

def resized_image(img, scale = 1.0):
  width = int(img.shape[1] * scale)
  height = int(img.shape[0] * scale)
  dim = (width, height)
  # resize image
  resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
  return resized