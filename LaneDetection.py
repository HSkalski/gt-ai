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
        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break


def screen_grab():
    img = np.asarray(sct.grab(monitor))
    return img


def process_img(img):
    #processedImg = img
    
    #Set region of intrest
    

    #Contour Scan
    imgray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    ret,thresh = cv2.threshold(imgray,127,255,0)
    img2, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    cv2.imshow("Contours", img2)
    #Line processing?
    edges = cv2.Canny(img2,50,150)
    cv2.imshow("Canny Edges", edges)

    #return processedImg
    return img

main()