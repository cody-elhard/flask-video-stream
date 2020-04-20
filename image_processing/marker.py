import cv2
import numpy as np
import random as rand

#constants
min_contour_size = 200 # 0 - 500?
hsv_value = 200 # 0 - 255

def angle(line):
    x1, y1, x2, y2 = line[0]
    x_diff = x1 - x2
    y_diff = y1 - y2
    radians = np.arctan2(x_diff, y_diff)
    return np.abs(np.degrees(radians))


def find_contours(img):
    contours, hierarchy = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    bounding_box = []

    for contour in contours:
        if len(contour) > min_contour_size:
            c = contour.squeeze(1)

            min_x = np.min(c[:, 0])
            max_x = np.max(c[:, 0])
            min_y = np.min(c[:, 1])
            max_y = np.max(c[:, 1])

            # bounding box of contour
            bounding_box.append((min_x, min_y, max_x, max_y))

    return bounding_box


def find_area_of_interest(markers):
    # markers = [[marker], [marker], [marker], ....]
    # marker = [topX, topY, btmX, btmY]
    img_points = []

    for i in range(0, len(markers), 2):

        top_marker = -1
        btm_marker = -1

        # if avg Y of markers[i] is greater than avg Y of markers[i+1] (i is lower in image)
        # then top_marker gets markers[ i + 1 ]
        if (markers[i][1] + markers[i][3]) / 2 > (markers[i + 1][1] + markers[i + 1][3]) / 2:
            top_marker = markers[i + 1]
            btm_marker = markers[i]
        else:
            top_marker = markers[i]
            btm_marker = markers[i + 1]

        # determine range of x
        left_x = min(top_marker[0], btm_marker[0])
        right_x = max(top_marker[2], btm_marker[2])

        # determine range of y
        top_y = max(top_marker[1], top_marker[3])
        btm_y = min(btm_marker[1], btm_marker[3])

        # the plus/minus 1 can be removed, but canny is
        # picking up the edges of the markers
        img_points.append((left_x, top_y + 1, right_x, btm_y - 1))

    #print(img_points)
    return img_points


def find_water_lvls(img, areas_of_interest):

    #img_points is a 2d array of 'AREAS' of Interest
    percents = []

    #for each area of interest
    for points in areas_of_interest:
        percent = find_water_lvl(img, points)
        percents.append(percent)

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
    edges = cv2.Canny(tube, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 15, minLineLength=(0.1 * x_diff))

    for line in lines:
        #only find one line that fits criteria
        if 85 <= angle(line) <= 100:

            x1, y1, x2, y2 = line[0]

            img_topY = points[1]
            img_btmY = points[3]

            lvl = round(((y1 + y2) / 2) / (img_btmY - img_topY), 4)
            percent = round(1 - lvl, 4)
            #print(percent*100)
            return percent



def process_image(img, hardcoded_image = False):
    if (hardcoded_image):
        img = cv2.imread('images/markers.jpg')

    # resize variables
    width = int(img.shape[1] * .5)
    height = int(img.shape[0] * .5)
    dim = (width, height)

    # allowed variance on yellow 
    yellow = [[0, 153, 153], [102, 255, 255]]
    lower = np.array(yellow[0])
    upper = np.array(yellow[1])

    # bitwise and with yellow
    mask = cv2.inRange(img, lower, upper)
    output = cv2.bitwise_and(img, img, mask=mask)

    # convert to grayscale
    gray = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 127, 255, 0)

    # find contours on markers
    bounding_boxes = find_contours(thresh)

    # structing the array allows for easy sorting
    dtype = [('TopX', int), ('TopY', int), ('BottomX', int), ('BottomY', int)]
    markers = np.array(bounding_boxes, dtype=dtype)
    markers = np.sort(markers, order='TopX')

    areas_of_interest = find_area_of_interest(markers)

    # same concept for the structure as bounding boxes
    # [topX, topY, btmX, btmY]
    img_points = np.array(areas_of_interest, dtype=dtype)

    # tubes = [len(img_points)]
    print('\nNumber of tubes detected: ' + str(len(img_points)))

    water_lvl_percents = find_water_lvls(img, img_points)

    print(water_lvl_percents)

    # floats up to 4 decimal places
    return water_lvl_percents


