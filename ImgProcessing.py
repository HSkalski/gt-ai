import cv2
import numpy as np 
import mss 

def nothing(x): #function that does nothing to satisfy trackbar
    pass

monitor = {"top": 40, "left": 0, "width": 800, "height": 640}
sct = mss.mss()

#Create Trackbars for contours
cv2.namedWindow('contour')
cv2.createTrackbar('x','contour',0,255,nothing)
cv2.createTrackbar('y','contour',0,255,nothing)

#Canny trackbars
cv2.namedWindow('canny')
cv2.createTrackbar('a','canny',0,255,nothing)
cv2.createTrackbar('b','canny',0,255,nothing)

###Create Trackbars for contours
cv2.namedWindow('mask')
cv2.createTrackbar('low','mask',0,255,nothing)
cv2.createTrackbar('high','mask',0,255,nothing)



def main():

    

    while 1:
        
        img = cv2.imread('desertroad.jpg')
        img = cv2.resize(img,(800,600),interpolation = cv2.INTER_CUBIC)

        processedImg = process_img(img)
        cv2.imshow("Original IMG", img)
        #cv2.imshow("Processed IMG", processedImg)
        if cv2.waitKey(25) & 0xFF == ord('q'): #if pressing q 
            cv2.destroyAllWindows()
            break


def process_img(img):
    
    #processedImg = img
    
    #Set region of intrest
    
    img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    ##Blur
    blur = cv2.blur(img,(6,6))
    cv2.imshow('blur 1', blur)
    # Canny
    canny = CannyScan(blur)
    cv2.imshow('canny',canny)
    # second blur
    #blur2 = cv2.blur(canny,(3,3))
    #cv2.imshow('blur 2',blur2)
    # contour
    contour = ContourFromCannyScan(canny)
    cv2.imshow('contour',contour)

    # mask = MaskScan(img)
    # cv2.imshow('mask',mask)
    # contour = ContourScan(mask)
    # cv2.imshow('contour',contour)
    # canny = CannyScan(contour)
    # cv2.imshow('canny',canny)

    
    ###############Line Processing?#######################
    #img = cv2.imread('desertroad.jpg')
    #gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    #edges = cv2.Canny(gray,50,150,apertureSize = 3)

    lines = cv2.HoughLines(canny,1,np.pi/180,200)
    print(len(lines))
    for rho,theta in lines[0]:
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + 1000*(-b))
        y1 = int(y0 + 1000*(a))
        x2 = int(x0 - 1000*(-b))
        y2 = int(y0 - 1000*(a))

        cv2.line(img,(x1,y1),(x2,y2),(0,0,255),2)

    cv2.imshow('houghlines3.jpg',img)

    minLineLength = 100
    maxLineGap = 10
    lines = cv2.HoughLinesP(canny,1,np.pi/180,100,minLineLength,maxLineGap)
    for x1,y1,x2,y2 in lines[0]:
        cv2.line(img,(x1,y1),(x2,y2),(0,255,0),2)

    cv2.imshow('houghlines5.jpg',img)

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







#        Notes on working values
#   mask: low: 0, high: 200
#   Contours: 160, 255
#
#
