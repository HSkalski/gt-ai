import cv2
import numpy as np 
import mss 

import time


def record():
    
    mon = {"top": 40, "left": 0, "width": 800, "height": 640}

    sct = mss.mss()
    last_time = time.time()
    while 1:

        img = np.asarray(sct.grab(mon))

        dt = time.time() - last_time
        print(dt)

        last_time = time.time()
        cv2.imshow("test",img)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break

record()