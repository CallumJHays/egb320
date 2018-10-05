import numpy as np
import cv2
from VisionSystem import VisionSystem, VisualObject
from VisionSystem.DetectionModel import ThreshBlob, Frame, ColorSpaces
from time import time

import os

index = ''

filepath = lambda: os.path.join(os.path.dirname(__file__), 'data', 'test_video' + index + '.avi')

# just track the ball for now
vision_system = VisionSystem({
    'ball': VisualObject(
        real_size=(0.043, 0.043, 0.043),
        detection_model=ThreshBlob.load("ball_model.threshblob.pkl"),
        result_limit=1
    )
})

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

out = cv2.VideoWriter(filepath(), fourcc, 20.0, (640, 480))
cap = cv2.VideoCapture(0)
frames_this_sec = 0
last_sec_fps = 0
last_sec_time = time()

while(cap.isOpened()):
    ret, img = cap.read()
    if ret==True:
        frame = Frame(img)
        vision_system.update_with_and_label_frame(frame)
        frames_this_sec += 1
        now_time = time()

        if now_time - last_sec_time >= 1:
            last_sec_time = now_time
            last_sec_fps = frames_this_sec
            frames_this_sec = 0

        frame.link_bgr(cv2.putText(
            frame.get(ColorSpaces.BGR),
            text="FPS: %d" % last_sec_fps,
            org=(0, 470),
            fontFace=cv2.FONT_HERSHEY_PLAIN,
            fontScale=1.5,
            color=(0, 255, 255)
        ))

        out.write(frame.get(ColorSpaces.BGR))

        cv2.imshow('frame', frame.get(ColorSpaces.BGR))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# Release everything if job is finished
cap.release()
out.release()
cv2.destroyAllWindows()