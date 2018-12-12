import cv2
import numpy as np 
import mss 
import random as rand

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
    lines = cv2.HoughLinesP(imgroi, 1, np.pi/180, 180, 20, 15)
    draw_lines(img,lines)
    
    cv2.imshow("graybulr",blur)
    cv2.imshow("Canny Edges", imgedges)
    cv2.imshow("Region of Interest", imgroi)
    #return processedImg
    return img

main()