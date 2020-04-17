import cv2
import threading
import time

from capture import capture_and_save

class Camera:
    def __init__(self, video_source=0):
        self.video_source = video_source
        self.camera = cv2.VideoCapture(self.video_source)

        # Setup background task
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
      while(True):
        print("image capture init")
        v, img = self.camera.read()
        if v:
          capture_and_save(img)
          print("image captured")

        time.sleep(3) # Wait a second so other stuff can happen

    # Need to implement / Add button to UI
    # def stop(self):

    def get_frame(self):
      img = cv2.imread("images/last.jpg")

      if (img.size == 0):
        return cv2.imread("images/not_found.jpeg")

      return img
