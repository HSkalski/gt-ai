import cv2
import numpy as np 
import mss 
import random as rand
from statistics import median
from statistics import mean
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

monitor = {"top": 40, "left": 0, "width": 800, "height": 640}
sct = mss.mss()




def nothing(x): #function that does nothing to satisfy trackbar
    pass
#Canny trackbars
cv2.namedWindow('Canny Edges')
cv2.createTrackbar('a','Canny Edges',0,1000,nothing)
cv2.createTrackbar('b','Canny Edges',0,1000,nothing)

def main():
    lane1 = [0,0]
    lane2 = [0,0]   
    while 1:
        img = screen_grab()
        processedImg,lane1,lane2 = process_img(img,lane1,lane2)
        cv2.imshow("Original IMG", img)
        #cv2.imshow("Processed IMG", processedImg)
        if cv2.waitKey(25) & 0xFF == ord('q'): #if pressing q 
            cv2.destroyAllWindows()
            break

#Region of interest function modified Medium.com article - 
# https://medium.com/@mrhwick/simple-lane-detection-with-opencv-bfeb6ae54ec0 
def region_of_interest(img, vertices):
    # Define a blank matrix that matches the image height/width.
    mask = np.zeros_like(img)
      
    # Fill inside the polygon
    cv2.fillPoly(mask, vertices, 255)
    
    # Returning the image only where mask pixels match
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image

def screen_grab():
    img = np.asarray(sct.grab(monitor))
    return img

def draw_eq(img,lane):
    try:
        cv2.line(img, (0,int(lane[1])), (800,int(lane[0]*800+lane[1])),[255,255,255],5)
    except Exception as e:
        print("Not drawing equation: ", str(e))

def draw_lines(img, lines):
    try:
        for line in lines:
            loc = line[0]
            m = slope(loc)
            if m > 0:
                cv2.line(img, (loc[0],loc[1]) , (loc[2],loc[3]) , [255] , 1 )
            else:
                cv2.line(img, (loc[0],loc[1]) , (loc[2],loc[3]) , [0,0,255] , 1 )
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
                for line in i:
                    x1 = line[0]
                    y1 = line[1]
                    x2 = line[2]
                    y2 = line[3]
                    m = slope(line)
                    b = Yint(line)
                    line_dict[count] = [m, b, x1, y1, x2, y2]
        # separate positive vs negative slopes while skipping small slopes
        for i in line_dict:
            if line_dict[i][0] > 0.1: # slope > 0 >>----> right
                right_lines.append(line_dict[i])
            elif line_dict[i][0] < -0.1: # slope <= 0 >>----> left
                left_lines.append(line_dict[i])
            else:
                pass
        # median slopes
        rms = [] #right slopes
        lms = [] #left slopes
        medRm = 0 #median right slope
        medLm = 0 #median left slope
        try:
            for line in right_lines:
                rms.append(line[0])
            medRm = median(rms)
            print("Right Slope Median: ", medRm)
        except:
            print("No Right Lines")
        try:
            for line in left_lines:
                lms.append(line[0])
            medLm = median(lms)
            print("Left Slope Median: ", medLm)
        except:
            print("No Left Lines")
        # remove outliers (slope)
        maxRm = medRm + (medRm*0.01) # max and min left and right slopes
        minRm = medRm - (medRm*0.01)
        maxLm = medLm - (medLm*0.01)
        minLm = medLm + (medLm*0.01)
        for i,line in enumerate(right_lines): # pop if out of range
            if line[0] > maxRm or line[0] < minRm:
                right_lines.pop(i)
        for i,line in enumerate(left_lines):
            if line[0] > maxLm or line[0] < minLm:
                left_lines.pop(i)
        # median Y intercepts
        rint = [] #right intercept
        lint = [] #left intercept
        medRint = 0 #median right intercept
        medLint = 0 #median left intercept
        try:
            for line in right_lines:
                rint.append(line[1])
            medRint = median(rint)
            print("Right Intercept Median: ", medRint)
        except:
            print("No Right Lines")
        try:
            for line in left_lines:
                lint.append(line[1])
            medLint = median(lint)
            print("Left Intercept Median: ", medLint)
        except:
            print("No Left Lines")
        print("Right Len pre int: ", len(right_lines))
        print("Left Len pre int: ", len(left_lines))
        #remove outliers (intercept)
        maxRint = medRint + (medRint*0.01) # max and min left and right intercepts
        minRint = medRint - (medRint*0.01)
        maxLint = medLint - (medLint*0.01)
        minLint = medLint + (medLint*0.01)
        for i,line in enumerate(right_lines): # pop if out of range
            if line[1] > maxRint or line[1] < minRint:
                right_lines.pop(i)
        for i,line in enumerate(left_lines):
            if line[1] > maxLint or line[1] < minLint:
                left_lines.pop(i)
        # Average of remaining lines - slope
        avgRms = []
        avgLms = []
        avgRm = 0
        avgLm = 0
        try:
            for line in right_lines:
                avgRms.append(line[0])
            avgRm = mean(avgRms)
            print("Right Average Slope: ", avgRm)
        except:
            pass
        try:
            for line in left_lines:
                avgLms.append(line[0])
            avgLm = mean(avgLms)
            print("Left Average Slope: ", avgLm)
        except:
            pass
        # Average of remaining lines - intercept
        avgRints = []
        avgLints = []
        avgRint = 0
        avgLint = 0
        try:
            for line in right_lines:
                avgRints.append(line[1])
            avgRint = median(avgRints)
            print("Right Average Slope: ", avgRint)
        except:
            pass
        try:
            for line in left_lines:
                avgLints.append(line[1])
            avgLint = median(avgLints)
            print("Left Average Slope: ", avgLint)
        except:
            pass
        ######################
        print("Right Len: ", len(right_lines))
        print("Left Len: ", len(left_lines))
        try:
            print("Left lines:")
            for i in left_lines:
                print("Left Line: ",i)
            print("right lines:")
            for i in right_lines:
                print("Right Line: ",i)
        except:
            pass
        
        try:
            for loc in left_lines:
                cv2.line(img, (loc[2],loc[3]) , (loc[4],loc[5]) , [0,165,255] , 1 )
        except:
            print("error showing left lines")
        try:
            for loc in right_lines:
                cv2.line(img, (loc[2],loc[3]) , (loc[4],loc[5]) , [0,165,255] , 1 )
        except:
            print("error showing right lines")
        ######################
        # find max Xs and Ys to use as lane
        ##right lane
        try:
            laneR = [avgRm,avgRint]
        except:
            print("Final Right Lane")
        ##left lane
        try:
            laneL = [avgLm,avgLint]
        except:
            print("Final Left Lane")
        print("Return: ",laneR,laneL)
        if laneR == []:
            laneR = [0,0]
        if laneL == []:
            laneL = [0,0]

        return laneR, laneL
    except Exception as e:
        print("Draw_lanes: ", str(e))
        return [0,0],[0,0]
        

def process_img(img,lane1,lane2):
    #processedImg = img
    
    #grayscale
    imgray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    #Canny Scan
    imgedges = cv2.Canny(imgray,  175,300)
    #imgedges = cv2.Canny(imgray, cv2.getTrackbarPos('a','Canny Edges'), cv2.getTrackbarPos('b','Canny Edges'))
    #Blur
    blur = cv2.blur(imgedges,(5,5))
    #region of interest
    points = [[10,500],[10,400],[350,200],[450,200],[790,400],[790,500]]


    roiVertices = np.array([points[0],points[1], points[2], points[3], points[4], points[5]], np.int32)

    #imgroi = roi(blur, [vertices])
    imgCrop = region_of_interest(blur,[roiVertices])

    cv2.line(img, (points[0][0],points[0][1]),(points[1][0],points[1][1]), [0,255,0], 3)
    cv2.line(img, (points[1][0],points[1][1]),(points[2][0],points[2][1]), [0,255,0], 3)
    cv2.line(img, (points[2][0],points[2][1]),(points[3][0],points[3][1]), [0,255,0], 3)
    cv2.line(img, (points[3][0],points[3][1]),(points[4][0],points[4][1]), [0,255,0], 3)
    cv2.line(img, (points[4][0],points[4][1]),(points[5][0],points[5][1]), [0,255,0], 3)
    cv2.line(img, (points[5][0],points[5][1]),(points[0][0],points[0][1]), [0,255,0], 3)

    #Lines
    minLineLength = 30 # 20
    maxLineGap = 15  #15
    lines = cv2.HoughLinesP(imgCrop, 1, np.pi/180, 180, minLineLength, maxLineGap)
    draw_lines(img,lines)
    newlane1,newlane2 = draw_lanes(img,lines)
    if newlane1 != [0,0]:
        lane1 = newlane1
    if newlane2 != [0,0]:
        lane2 = newlane2

    
    print("------------------------")
    print(lane1)
    print(lane2)
    print(newlane1)
    print(newlane2)
    print("------------------------")
    try:
        #right
        #cv2.line(img,(lane1[0],lane1[1]),(lane1[2],lane1[3]),[0,255,255], 3)
        #temporary
        draw_eq(img,lane1)
    except:
        print("No new Right Lane to print: main()")
    try:
        #left
        #cv2.line(img,(lane2[0],lane2[1]),(lane2[2],lane2[3]),[255,0,100], 3)
        #temporary
        draw_eq(img,lane2)
    except:
        print("No new Left Lane to print: main()")
    

    cv2.imshow("graybulr",blur)
    cv2.imshow("Canny Edges", imgedges)
    cv2.imshow("Region of Interest", imgCrop)
    #return processedImg
    return img, lane1, lane2

main()