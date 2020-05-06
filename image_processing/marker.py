import cv2, json, os, datetime
import numpy as np
import random as rand

from example_output import GenerateOutput

#constants
min_contour_size = 110 # 0 - 500?
hsv_value = 200 # 0 - 255
scale = 2
cushion = 7
k_blur = 25


def angle(line):
    x1, y1, x2, y2 = line[0]
    x_diff = x1 - x2
    y_diff = y1 - y2
    radians = np.arctan2(x_diff, y_diff)
    return np.abs(np.degrees(radians))


def find_water_lvls(img, areas_of_interest):
    # img_points is a 2d array of 'AREAS' of Interest
    percents = []
    # for each area of interest
    for points in areas_of_interest:
        try:
            percent = find_water_lvl(img, points)
            percents.append(percent)
        except:
            print("error detecting water lvl, adding 0 to : " + str(percents))
            percents.append(int(0))

    try:
      current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      if( os.stat("data.json").st_size == 0):
        with open("data.json", "w") as outfile:
          # json.dump([[current_time, GenerateOutput(20)]], outfile, indent=2) # Use this for fake data
          json.dump([[current_time, percents]], outfile, indent=2) # Use this for real data
      else:
        with open("data.json") as outfile:
          old_data = json.load(outfile)
        # new_data = [[current_time, GenerateOutput(20)]] # Use this for fake data
        new_data = [[current_time, percents]] # Use this for real data

        # old_data.append(new_data)  # Leaving this here because it cost me 3 hours.

        old_data = new_data + old_data

        with open("data.json", "w") as outfile:
          json.dump(old_data, outfile, indent=2)
    except:
      print("Error handling JSON")
    

    return percents



def find_water_lvl(img, points):

    # points represents area of interest
    # i.e. under top marker and above bottom marker
    pts_one = np.float32([[points[0], points[1]],  # leftX  topY
                          [points[2], points[1]],  # rightX topY
                          [points[0], points[3]],  # leftX  btmY
                          [points[2], points[3]]])  # rightX btmY

    x_diff = points[2] - points[0]
    y_diff = points[3] - points[1]

    pts_two = np.float32([[0, 0],
                          [x_diff, 0],
                          [0, y_diff],
                          [x_diff, y_diff]])

    matrix = cv2.getPerspectiveTransform(pts_one, pts_two)
    tube = cv2.warpPerspective(np.copy(img), matrix, (x_diff, y_diff))

    # get edges on the tube (cropped image)
    # might need gray scale/median filter?
    tube_blur = cv2.medianBlur(tube, 7)
    edges = cv2.Canny(tube_blur, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 15, minLineLength=(0.1 * x_diff))

    if lines is not None:
        for line in lines:
            #only find one line that fits criteria
            if 85 <= angle(line) <= 100:
                x1, y1, x2, y2 = line[0]

                # DEBUG PURPOSE #
                # cv2.line(display_img, (points[0], y1+points[1]), (x2+points[0], y2+points[1]), (255, 0, 0), 5)

                img_topY = points[1]
                img_btmY = points[3]

                lvl = round(((y1 + y2) / 2) / (img_btmY - img_topY), 4)
                percent = round(1 - lvl, 4)
                if percent is None:
                    return 0.0
                return percent
        return 0.0
    else:
        print("No lines detected")
        return 0.0



def find_areas_of_interest(markers, avg_y):
    cropping_points = []
    for i in range(0, len(markers), 2):
        top_marker = -1
        btm_marker = -1

        # if markers[i] y is greater than avg_y (i is lower in image)
        # then top_marker gets markers[ i + 1 ]
        if markers[i][1] > avg_y:
            top_marker = markers[i + 1]
            btm_marker = markers[i]
        else:
            top_marker = markers[i]
            btm_marker = markers[i + 1]

        # determine range of x
        left_x = min(top_marker[0], btm_marker[0])
        right_x = max(top_marker[2] + top_marker[0], btm_marker[2] + btm_marker[0])

        # determine range of y
        # the plus/minus 1 can be removed, but canny is
        # picking up the edges of the markers
        top_y = top_marker[1] + top_marker[3] + cushion
        btm_y = btm_marker[1] - cushion
        
        # DEBUG PURPOSE #
        #cv2.rectangle(display_img, (left_x, top_y), (right_x, btm_y), (0, 255, 255), 3)

        cropping_points.append((left_x, top_y, right_x, btm_y))

    return cropping_points



def process_image(img, hardcoded_image = False, should_return_image = False):
    if (hardcoded_image):
      img = cv2.imread('images/markers.jpg')
    
    display_img = img.copy()
    dim = (int(scale * img.shape[1]), int(scale * img.shape[0]))

    blur = cv2.medianBlur(img, k_blur)

    hsv_lower = (0, 0, hsv_value)
    hsv_upper = (179, 255, 255)

    mask = cv2.inRange(blur, hsv_lower, hsv_upper)

    # DEBUG PURPOSE #
    # cv2.imshow("Mask", cv2.resize(mask, dim))

    contours, hierarchy = cv2.findContours(mask, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

    # find average area of contours
    avg_area = 0
    for contour in contours:
        area = cv2.contourArea(contour)
        avg_area += area

    # calc avg area
    num_contours = len(contours)
    if len(contours) <= 0:
        num_contours = 1
    avg_area = int(avg_area / num_contours)

    # filter by area and find average y
    filtered_contours = []
    avg_y = 0
    for contour in contours:
        if cv2.contourArea(contour) > .5 * avg_area:
            rect = cv2.boundingRect(contour)
            # rect = (topX, topY, topX + this, topY + this)
            avg_y += int((rect[1] + rect[3] + rect[1]) / 2)
            filtered_contours.append(rect)

    # calc avg y
    if len(filtered_contours) <= 0:
        filtered_contours.append(1)
    avg_y = int(avg_y / len(filtered_contours))

    # DEBUG #
    # cv2.line(display_img, (0, avg_y), (display_img.shape[1], avg_y), (0, 255, 0), 10)

    # DEBUG PURPOSE #
    # find avg distance apart
    # avg_distance_apart = 0
    # for box in filtered_contours:
    #     y = 1
    #     try:
    #         y = box[1]
    #     except:
    #         print('Some error')
    #     if int(y) / 2 < avg_y:
    #         min_d = 100000
    #         for next_box in filtered_contours:
    #             if next_box != box and (next_box[1] + next_box[3] + next_box[1]) / 2 < avg_y:
    #                 distance_apart = math.fabs(int((next_box[0] + next_box[2]) / 2) - int((box[0] + box[2]) / 2))
    #                 if distance_apart < min_d:
    #                     min_d = distance_apart
    #         avg_distance_apart += min_d

    # calc average distance apart
    # avg_distance_apart = int(avg_distance_apart / 6)

    # build np array for sorting
    dtype = [('TopX', int), ('TopY', int), ('BottomX', int), ('BottomY', int)]
    markers = np.array(filtered_contours, dtype=dtype)
    markers = np.sort(markers, order='TopX')

    # DEBUG PURPOSE #
    # draw bounding boxes
    # y = 200
    # for box in markers:
    #     if (box[1] + box[3] + box[1]) / 2 < avg_y:
    #         cv2.rectangle(display_img, (box[0], box[1]), (box[0] + box[2], box[1] + box[3]), (255, 0, 0), 3)
    #         cv2.line(display_img, (box[0] + box[2], y), (box[0] + box[2] + avg_distance_apart, y), (255, 255, 0), 5)
    #         y += 10
    #     else:
    #         cv2.rectangle(display_img, (box[0], box[1]), (box[0] + box[2], box[1] + box[3]), (0, 0, 255), 3)

    water_lvl_percents = [0.0]

    try:
      # find points to crop tubes
      areas_of_interest = find_areas_of_interest(markers, avg_y)
    except:
      print("Error finding areas of interest")
      if should_return_image:
          return display_img
      else:
          return water_lvl_percents

    try:
      # try and find water lvls
      water_lvl_percents = find_water_lvls(img, areas_of_interest)
      # print(water_lvl_percents)
    except:
      print("Error find water levels")
      if should_return_image:
          return display_img
      else:
          return water_lvl_percents

    try:
      #try and draw text on img
      for index, points in enumerate(areas_of_interest):
        (topX, topY, btmX, btmY) = points

        # Write the percentage over the test tube
        cv2.putText(
          display_img,
          "{}%".format(str(round(water_lvl_percents[index] * 100, 2))),
          (
            int(topX), # Align left
            int((topY + btmY) / 2) # Center vertically
          ),
          cv2.FONT_HERSHEY_SIMPLEX,
          0.9,
          (0, 0, 255),
          2,
          cv2.LINE_AA
        )
    except:
      print("Error drawing text on image")
      if should_return_image:
        return display_img
      else:
        return water_lvl_percents
        

    # DEBUG PURPOSE #
    # cv2.imshow("Image", cv2.resize(display_img, dim))
    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break

    # floats up to 4 decimal places
    if should_return_image:
      return display_img
    else:
      return water_lvl_percents


