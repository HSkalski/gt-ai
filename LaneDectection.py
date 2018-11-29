import cv2
import numpy as np 
import mss 

monitor = {"top": 40, "left": 0, "width": 800, "height": 640}
sct = mss.mss()

def main():
    while 1:
        img = screen_grab()
        
        cv2.imshow("Lane Detection", img)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break


def screen_grab():
    img = np.asarray(sct.grab(monitor))
    return img


#def process_img():

    #Set region of intrest

    #Contour Scan


main()