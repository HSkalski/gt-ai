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
    blur = cv2.blur(img,(5,5))
    
    imgray = cv2.cvtColor(blur,cv2.COLOR_BGR2GRAY)
    cv2.imshow("graybulr",imgray)
    #Set region of intrest
    
    # #Mask
    # ### Set Color space 
    # #######hsv = cv2.cvtColor(imgray,cv2.COLOR_RGB2HSV)
    # ### create mask
    # lower_gray = np.array([0])
    # upper_gray = np.array([200])
    # mask = cv2.inRange(imgray,lower_gray,upper_gray)
    # ### invert mask
    # mask = cv2.bitwise_not(mask)
    # cv2.imshow("mask",mask)
    # ### Bitwise-AND mask with original image
    # res = cv2.bitwise_and(img,img,mask = mask)

    #Canny Scan
    imgedges = cv2.Canny(imgray,50,150)
    cv2.imshow("Canny Edges", imgedges)

    #Contour Scan
    imgcontour, contours, hierarchy = cv2.findContours(imgedges,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    cv2.imshow("Contours", imgcontour)

    

    #Line Processing?
    minLineLength = 50
    maxLineGap = 10
    lines = cv2.HoughLinesP(imgedges,1,np.pi/180,100,minLineLength,maxLineGap)
    print(len(lines))
    for x1,y1,x2,y2 in lines[0]:
        cv2.line(img,(x1,y1),(x2,y2),(0,255,0),2)



    #return processedImg
    return img

main()