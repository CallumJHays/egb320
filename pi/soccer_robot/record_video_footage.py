import numpy as np
import cv2

cap = cv2.VideoCapture(0)

import os

index = ''

filepath = lambda: os.path.join(os.path.dirname(__file__), 'data', 'test_video' + index + '.avi')

while True:
    if os.path.isfile(filepath()):
        if index:
            index = '('+str(int(index[1:-1])+1)+')' # Append 1 to number in brackets
        else:
            index = '(1)'
        pass # Go and try create file again
    else:
        break

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')

out = cv2.VideoWriter(filepath(), fourcc, 20.0, (640,480))

while(cap.isOpened()):
    ret, frame = cap.read()
    if ret==True:
        out.write(frame)

        cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# Release everything if job is finished
cap.release()
out.release()
cv2.destroyAllWindows()