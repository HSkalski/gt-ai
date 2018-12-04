import cv2
import numpy as np 
import mss 

monitor = {"top": 40, "left": 0, "width": 800, "height": 640}
sct = mss.mss()

def main():
    while 1:
        img = screen_grab()
        processedImg = process_img(img)
        cv2.imshow("Original IMG", img)
        #cv2.imshow("Processed IMG", processedImg)
        if cv2.waitKey(25) & 0xFF == ord('q'): #if pressing q 
            cv2.destroyAllWindows()
            break


def screen_grab():
    img = np.asarray(sct.grab(monitor))
    return img


def process_img(img):
    #processedImg = img
    
    #Set region of intrest
    
    #### Mask ###
    # convert to hsv
    hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    # upper / lower bounds
    lower_gray = np.array([0,0,0])
    upper_gray = np.array([200,200,200])
    # create mask
    mask = cv2.inRange(hsv,lower_gray,upper_gray)
    # invert mask
    mask = cv2.bitwise_not(mask)
    # Bitwise-AND mask with image
    res = cv2.bitwise_and(img,img,mask = mask)
    
    cv2.imshow('res',res)

    #Contour Scan
    imgray = cv2.cvtColor(res,cv2.COLOR_BGR2GRAY)
    ret,thresh = cv2.threshold(imgray,160,255,0)
    imgcontour, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    cv2.imshow("Contours", imgcontour)

    #Canny Scan
    imgedges = cv2.Canny(imgcontour,50,150)
    cv2.imshow("Canny Edges", imgedges)

    #Line Processing?


    #return processedImg
    return img

main()