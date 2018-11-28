import cv2
import numpy as np 
import mss 

def record():
    
    mon = {"top": 40, "left": 0, "width": 800, "height": 640}

    sct = mss.mss()

    while 1:
        img = np.asarray(sct.grab(mon))

        cv2.imshow('Test',img)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break

record()