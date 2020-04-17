import cv2
import numpy as np
import random as rand

def angle(line):
    x1, y1, x2, y2 = line[0]
    x_diff = x1 - x2
    y_diff = y1 - y2
    radians = np.arctan2(x_diff, y_diff)
    return np.abs(np.degrees(radians))

def process_image(img, hardcoded_image = False):
  if (hardcoded_image):
    img = cv2.imread('images/markers.jpg')

  #resize variables
  width = int(img.shape[1] * .5)
  height = int(img.shape[0] * .5)
  dim = (width, height)

  # allowed variance on green/yellow #
  yellow = [[0, 153, 153], [102, 255, 255]]
  green = [[4,69,0], [118,185,4]]
  lower = np.array(yellow[0])
  upper = np.array(yellow[1])

  # bitwise and with green/yellow
  mask = cv2.inRange(img, lower, upper)
  output = cv2.bitwise_and(img, img, mask=mask)

  #black image
  blank_image = np.zeros(shape=[img.shape[0], img.shape[1], 3], dtype=np.uint8)

  ########################################################

  # convert to grayscale
  gray = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
  ret, thresh = cv2.threshold(gray, 127, 255, 0)

  # find contours on markers
  contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
  bounding_box = []
  for contour in contours:
      colorR = rand.randint(0 , 255)
      colorG = rand.randint(0, 255)
      colorB = rand.randint(0, 255)
      if len(contour) > 200:
          c = contour.squeeze(1)
          min_x = np.min(c[:, 0])
          max_x = np.max(c[:, 0])
          min_y = np.min(c[:, 1])
          max_y = np.max(c[:, 1])

          #bounding box of contour
          start = (min_x, min_y)
          end = (max_x, max_y)
          bounding_box.append((min_x, min_y, max_x, max_y))

          #show bounding box
          cv2.rectangle(img, start, end, (0, 255, 0), 4)

          #show contours
          cv2.drawContours(blank_image, contour, -1, (colorR, colorG, colorB), 3)

  #structing the array allows for easy sorting
  dtype = [('TopX', int), ('TopY', int), ('BottomX', int), ('BottomY', int)]
  bounding_box = np.array(bounding_box, dtype=dtype)
  bounding_box = np.sort(bounding_box, order='TopX')
  print(bounding_box)

  img_points = []

  for i in range(0, len(bounding_box), 2):
      top_marker = -1
      btm_marker = -1

      #if avg Y of i is greater than avg Y of i+1 (i is lower in image)
      #then top_marker gets i + 1
      if (bounding_box[i][1] + bounding_box[i][3])/2 > (bounding_box[i+1][1] + bounding_box[i+1][3])/2:
          top_marker = bounding_box[i + 1]
          btm_marker = bounding_box[i]
      else:
          top_marker = bounding_box[i]
          btm_marker = bounding_box[i + 1]

      #determine range of x
      left_x = min(top_marker[0], btm_marker[0])
      right_x = max(top_marker[2], btm_marker[2])

      #determine range of y
      top_y = max(top_marker[1], top_marker[3])
      btm_y = min(btm_marker[1], btm_marker[3])

      #the plus/minus 5 can be removed, but canny is
      #picking up the edges of the markers
      img_points.append((left_x, top_y+5, right_x, btm_y-5))
      #img_points.append((left_x, top_y, right_x, btm_y))
      #cv2.rectangle(img, (left_x, top_y), (right_x, btm_y), (0, 0, 255), 4)

  #same concept for the structure as bounding boxes
  img_points = np.array(img_points, dtype=dtype)
  #tubes = [len(img_points)]
  print('\nNumber of tubes: ' + str(len(img_points)))
  for points in img_points:
      #points represents area of interest
      #i.e. under top marker and above bottom marker
      pts_one = np.float32([[points[0], points[1]],  # leftX  topY
                            [points[2], points[1]],  # rightX topY
                            [points[0], points[3]],  # leftX  btmY
                            [points[2], points[3]]]) # rightX btmY

      x_diff = points[2] - points[0]
      y_diff = points[3] - points[1]

      pts_two = np.float32([[0, 0],
                            [x_diff, 0],
                            [0, y_diff],
                            [x_diff, y_diff]])

      matrix = cv2.getPerspectiveTransform(pts_one, pts_two)
      tube = cv2.warpPerspective(np.copy(img), matrix, (x_diff, y_diff))
      #tubes.append(tube)

      #get edges on the tube
      #might need gray scale/median filter?
      edges = cv2.Canny(tube, 50, 150)

      #find a horizontal line
      #minLength is 10% of width of tube
      lines = cv2.HoughLinesP(edges, 1, np.pi/180, 15, minLineLength=(0.1*x_diff))

      percentages = []
      for line in lines:
        x1, y1, x2, y2 = line[0]

        #transform the points on original image
        x1 += points[0]
        x2 += points[0]
        y1 += points[1]
        y2 += points[1]
        if 85 <= angle(line) <= 95:
          #draw line the entire width of tube
          cv2.line(img, (points[0], y1), (points[2], y2), (255, 0, 0), 7)

        y_diff = points[3] - points[1]
        line_height = points[1]
        # print("tube height")
        # print(y_diff)
        # print("water height")
        # print((((y1 + y2) / 2) - points[1]))
        percentage = (((y1 + y2) / 2) - points[1]) / y_diff
        percentages.append(percentage)

      print("percentage: {}".format(np.median(percentages)))

  return cv2.resize(img, dim)
