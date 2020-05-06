import cv2, threading, time

from capture import capture_and_save

class Camera:
    def __init__(self, static_file_path, video_source=0):
      self.video_source = video_source
      self.camera = cv2.VideoCapture(self.video_source)
      self.static_file_path = static_file_path

      # Setup background task
      thread = threading.Thread(target=self.run, args=())
      thread.daemon = True
      # print("start thread???")
      thread.start()

    def run(self):
      while(True):
        # print("read image")
        #img = cv2.imread(self.static_file_path)
        #if (img.size == 0):
        img = -1
        if(self.static_file_path):
          print("loading static image")
          img = cv2.imread("images/marker-3.jpg")
        else:
          img = cv2.imread("images/marker-3.jpg")

        capture_and_save(img)
        time.sleep(3) # Wait a second so other stuff can happen

    # Need to implement / Add button to UI
    # def stop(self):

    def get_frame(self):
      img = cv2.imread("images/last.jpg")

      if (img.size == 0):
        return cv2.imread("images/not_found.jpeg")

      return img
