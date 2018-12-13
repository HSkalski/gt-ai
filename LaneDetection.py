import cv2
import numpy as np 
import mss 
import random as rand
from statistics import median

monitor = {"top": 40, "left": 0, "width": 800, "height": 640}
sct = mss.mss()


# def nothing(x): #function that does nothing to satisfy trackbar
#     pass
# #Canny trackbars
# cv2.namedWindow('Canny Edges')
# cv2.createTrackbar('a','Canny Edges',0,1000,nothing)
# cv2.createTrackbar('b','Canny Edges',0,1000,nothing)

def main():
    while 1:
        img = screen_grab()
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

def screen_grab():
    img = np.asarray(sct.grab(monitor))
    return img

def draw_lines(img, lines):
    try:
        for line in lines:
            loc = line[0]
            cv2.line(img, (loc[0],loc[1]) , (loc[2],loc[3]) , [255,0,0] , 3 )
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

def draw_lanes(img, lines):
    try:
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
    except:
        return [0,0,0,0],[0,0,0,0]
        print("no lines")

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
    vertices = np.array([[10,500],[10,300], [300,200], [500,200], [800,300], [800,500]], np.int32)
    imgroi = roi(blur, [vertices])

    cv2.line(img, (10,500),(10,300), [0,255,0], 3)
    cv2.line(img, (300,200),(10,300), [0,255,0], 3)
    cv2.line(img, (300,200),(500,200), [0,255,0], 3)
    cv2.line(img, (500,200),(800,300), [0,255,0], 3)
    cv2.line(img, (800,300),(800,500), [0,255,0], 3)
    cv2.line(img, (800,500),(10,500), [0,255,0], 3)

    #Lines
    minLineLength = 30 # 20
    maxLineGap = 15  #15
    lines = cv2.HoughLinesP(imgroi, 1, np.pi/180, 180, minLineLength, maxLineGap)
    draw_lines(img,lines)
    lane1 = [0,0,0,0]
    lane2 = [0,0,0,0]
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

main()