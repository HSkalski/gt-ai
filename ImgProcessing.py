import cv2
import numpy as np 
import mss 
from statistics import median

def nothing(x): #function that does nothing to satisfy trackbar
    pass

monitor = {"top": 40, "left": 0, "width": 800, "height": 640}
sct = mss.mss()

# #Create Trackbars for contours
# cv2.namedWindow('contour')
# cv2.createTrackbar('x','contour',0,255,nothing)
# cv2.createTrackbar('y','contour',0,255,nothing)

# #Canny trackbars
# cv2.namedWindow('canny')
# cv2.createTrackbar('a','canny',0,255,nothing)
# cv2.createTrackbar('b','canny',0,255,nothing)

# ###Create Trackbars for contours
# cv2.namedWindow('mask')
# cv2.createTrackbar('low','mask',0,255,nothing)
# cv2.createTrackbar('high','mask',0,255,nothing)

def main():
    
    

    while 1:
        
        img = cv2.imread('plainroad3.jpg')
        img = cv2.resize(img,(800,600),interpolation = cv2.INTER_CUBIC)

        processedImg = process_img(img)
        cv2.imshow("Original IMG", img)
        #cv2.imshow("Processed IMG", processedImg)
        if cv2.waitKey(25) & 0xFF == ord('q'): #if pressing q 
            cv2.destroyAllWindows()
            break

def roi(img, vertices):
    mask = np.zeros_like(img)
    cv2.fillPoly(mask, vertices, 255)
    masked = cv2.bitwise_and(img, mask)
    return masked

def draw_lines(img, lines):
    try:
        for line in lines:
            loc = line[0]
            m = slope(loc)
            if m > 0:
                cv2.line(img, (loc[0],loc[1]) , (loc[2],loc[3]) , [255,0,0] , 3 )
            else:
                cv2.line(img, (loc[0],loc[1]) , (loc[2],loc[3]) , [0,0,255] , 3 )
            
    except:
        print("no lines found")

#
# y = mx+b
# y = slope x + yint
def slope(line):
    x1 = line[0]
    y1 = line[1] 
    x2 = line[2]
    y2 = line[3]
    m = (y2-y1)/(x2-x1)
    return m

def Yint(line):
    x1 = line[0]
    y1 = line[1] 
    x2 = line[2]
    y2 = line[3]
    m = (y2-y1)/(x2-x1)
    y = -x1*m+y1
    return y
############################################################################################################################

def draw_lanes(img, lines):
    
    line_dict = {}
    left_lines = []
    right_lines = []
    laneR = []
    laneL = []

    # add slope, y int, line points to dictionary
    for count,i in enumerate(lines):
            for xyxy in i:
                #stuff happens
                
                x1 = xyxy[0]
                y1 = xyxy[1]
                x2 = xyxy[2]
                y2 = xyxy[3]
                m = slope(xyxy)
                b = Yint(xyxy)
                line_dict[count] = [m, b, x1, y1, x2, y2]

    # separate positive vs negative slopes
    for i in line_dict:
        if line_dict[i][0] > 0: # slope > 0 >>----> right
            right_lines.append(line_dict[i])
        else: # slope <= 0 >>----> left
            left_lines.append(line_dict[i])

    # median slopes 
    rms = [] #right slopes
    lms = [] #left slopes
    medRm = 0 #median right slope
    medLm = 0 #median left slope
    for line in right_lines:
        rms.append(line[0])
    medRm = median(rms)
    for line in left_lines:
        lms.append(line[0])
    medLm = median(lms)

    # remove outliers 
    maxRm = medRm + (medRm*0.1) # max and min left and right slopes
    minRm = medRm - (medRm*0.1)
    maxLm = medLm - (medLm*0.1)
    minLm = medLm + (medLm*0.1)
    for i,line in enumerate(right_lines): # pop if out of range
        if line[0] > maxRm or line[0] < minRm:
            right_lines.pop(i)

    for i,line in enumerate(left_lines):
        if line[0] > maxLm or line[0] < minLm:
            left_lines.pop(i)

    # find max Xs and Ys to use as lane
    ##right lane
    Rxs = []
    Rys = []
    for line in right_lines:
        Rxs.append(line[2])
        Rxs.append(line[4])
        Rys.append(line[3])
        Rys.append(line[5])
    maxRx = max(Rxs)
    maxRy = max(Rys)
    minRx = min(Rxs)
    minRy = min(Rys)
    laneR = [minRx,minRy,maxRx,maxRy]
    ##left lane
    Lxs = []
    Lys = []
    for line in left_lines:
        Lxs.append(line[2])
        Lxs.append(line[4])
        Lys.append(line[3])
        Lys.append(line[5])
    maxLx = max(Lxs)
    maxLy = max(Lys)
    minLx = min(Lxs)
    minLy = min(Lys)
    laneL = [minLx,maxLy,maxLx,minLy]

    # for i in line_dict:
    #     print("#",i,": ",line_dict[i][0])
    # print("----------------------------")
    # for m in lms:
    #     print(m)

    return laneR, laneL

         

############################################################################################################################

def process_img(img):
    #processedImg = img
    
    #grayscale
    imgray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    #Canny Scan
    imgedges = cv2.Canny(imgray,  200,300)
    #imgedges = cv2.Canny(imgray, cv2.getTrackbarPos('a','Canny Edges'), cv2.getTrackbarPos('b','Canny Edges'))
    #Blur
    blur = cv2.blur(imgedges,(5,5))
    #region of interest
    #vertices = np.array([[10,500],[10,300], [300,200], [500,200], [800,300], [800,500]], np.int32)
    
    points = [[10,500],[10,400],[350,200],[450,200],[790,400],[790,500]]


    vertices = np.array([points[0],points[1], points[2], points[3], points[4], points[5]], np.int32)
    imgroi = roi(blur, [vertices])

    cv2.line(img, (points[0][0],points[0][1]),(points[1][0],points[1][1]), [0,255,0], 3)
    cv2.line(img, (points[1][0],points[1][1]),(points[2][0],points[2][1]), [0,255,0], 3)
    cv2.line(img, (points[2][0],points[2][1]),(points[3][0],points[3][1]), [0,255,0], 3)
    cv2.line(img, (points[3][0],points[3][1]),(points[4][0],points[4][1]), [0,255,0], 3)
    cv2.line(img, (points[4][0],points[4][1]),(points[5][0],points[5][1]), [0,255,0], 3)
    cv2.line(img, (points[5][0],points[5][1]),(points[0][0],points[0][1]), [0,255,0], 3)

    #Lines
    minLineLength = 30 # 20
    maxLineGap = 15  #15
    lines = cv2.HoughLinesP(imgroi, 1, np.pi/180, 180, minLineLength, maxLineGap)
    draw_lines(img,lines)

    lane1,lane2 = draw_lanes(img,lines)
    #right
    cv2.line(img,(lane1[0],lane1[1]),(lane1[2],lane1[3]),[255,0,200], 3)
    #left
    cv2.line(img,(lane2[0],lane2[1]),(lane2[2],lane2[3]),[255,0,100], 3)

    cv2.imshow("graybulr",blur)
    cv2.imshow("Canny Edges", imgedges)
    cv2.imshow("Region of Interest", imgroi)
    #return processedImg
    return img



def MaskScan(img):

    ### Set Color space 
    hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)

    ### upper and lower white/gray colors
    low = cv2.getTrackbarPos('low','mask')
    high = cv2.getTrackbarPos('high','mask')
    lower_gray = np.array([low,low,low])
    upper_gray = np.array([high,high,high])
    
    ### create mask
    mask = cv2.inRange(hsv,lower_gray,upper_gray)
    
    ### invert mask
    mask = cv2.bitwise_not(mask)

    ### Bitwise-AND mask with original image
    res = cv2.bitwise_and(img,img,mask = mask)

    return res

def ContourScan(img):
    #Contour Scan
    x = cv2.getTrackbarPos('x','contour')
    y = cv2.getTrackbarPos('y','contour')

    #imgray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    #ret,thresh = cv2.threshold(imgray,127,255,0)
    ret,thresh = cv2.threshold(imgray,  x,  y, 0)
    
    imgcontour, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    return imgcontour

def ContourFromCannyScan(img):
    #Contour Scan
    x = cv2.getTrackbarPos('x','contour')
    y = cv2.getTrackbarPos('y','contour')

    #imgray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    #ret,thresh = cv2.threshold(imgray,127,255,0)
    #ret,thresh = cv2.threshold(imgray,  x,  y, 0)
    
    imgcontour, contours, hierarchy = cv2.findContours(img,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    return imgcontour


def CannyScan(img):
    #Canny Scan

    a = cv2.getTrackbarPos('a','canny')
    b = cv2.getTrackbarPos('b','canny')

    #imgedges = cv2.Canny(imgcontour,50,150)
    imgedges = cv2.Canny(img, a, b)

    return imgedges


main()

# 0 :  [-1.0, 593.0, 93, 500, 259, 334]
# 1 :  [0.5827338129496403, -26.359712230215848, 651, 353, 790, 434]
# 2 :  [0.5538461538461539, -10.538461538461547, 660, 355, 790, 427]
# 3 :  [0.5325443786982249, 1.6923076923076792, 455, 244, 624, 334]
# 4 :  [-1.0, 603.0, 105, 498, 240, 363]
# 5 :  [-1.0, 589.0, 110, 479, 155, 434]
# 6 :  [-1.0, 600.0, 125, 475, 285, 315]
# 7 :  [-1.0, 595.0, 226, 369, 283, 312]
# 8 :  [0.5545454545454546, -13.03636363636366, 514, 272, 624, 333]
# 9 :  [0.5252525252525253, 7.010101010100982, 455, 246, 554, 298]
# 10 :  [0.5333333333333333, -4.933333333333337, 493, 258, 508, 266]
# 11 :  [-1.0, 606.0, 112, 494, 139, 467]
# 12 :  [0.5769230769230769, -23.576923076923038, 469, 247, 547, 292]
# 13 :  [0.5511811023622047, -12.433070866141748, 663, 353, 790, 423]
# 14 :  [0.5827338129496403, -23.359712230215848, 651, 356, 790, 437]
# 15 :  [0.5514705882352942, -7.661764705882376, 654, 353, 790, 428]
# 16 :  [0.5755395683453237, -19.676258992805742, 651, 355, 790, 435]
# 17 :  [-1.0, 619.0, 161, 458, 220, 399]
# 18 :  [-1.0, 606.0, 165, 441, 187, 419]
# 19 :  [-1.1986301369863013, 668.0, 146, 493, 292, 318]
# 20 :  [-1.0, 595.0, 95, 500, 205, 390]
# 21 :  [-1.0, 589.0, 164, 425, 258, 331]
# 22 :  [-1.1932773109243697, 668.6302521008404, 174, 461, 293, 319]
# 23 :  [-1.193103448275862, 665.1931034482759, 146, 491, 291, 318]
# 24 :  [0.5285714285714286, 6.428571428571445, 720, 387, 790, 424]
# 25 :  [-1.1666666666666667, 663.8333333333334, 275, 343, 293, 322]
# 26 :  [0.5566037735849056, -9.160377358490564, 683, 371, 789, 430]
# 27 :  [-1.0, 606.0, 227, 379, 262, 344]
# 28 :  [-1.1971830985915493, 672.056338028169, 193, 441, 264, 356]
# 29 :  [-1.0975609756097562, 636.1463414634146, 186, 432, 268, 342]
# 30 :  [-1.2222222222222223, 668.8888888888889, 202, 422, 220, 400]
# 31 :  [-1.0238095238095237, 604.452380952381, 103, 499, 145, 456]
# 32 :  [0.5526315789473685, -14.842105263157919, 586, 309, 624, 330]
# 33 :  [-1.1428571428571428, 649.2857142857142, 177, 447, 205, 415]
# 34 :  [-0.9767441860465116, 586.0232558139535, 171, 419, 257, 335]
# 35 :  [-1.0465116279069768, 614.2558139534884, 242, 361, 285, 316]
# 36 :  [0.575, -16.899999999999977, 492, 266, 532, 289]
# 37 :  [-1.0, 594.0, 94, 500, 282, 312]
# 38 :  [0.5606060606060606, -17.818181818181813, 558, 295, 624, 332]
# 39 :  [-1.0, 597.0, 145, 452, 285, 312]
# 40 :  [-0.9523809523809523, 598.2380952380952, 142, 463, 163, 443]
# 41 :  [0.5737704918032787, -20.73770491803276, 559, 300, 620, 335]
# 42 :  [-1.0, 609.0, 270, 339, 285, 324]
