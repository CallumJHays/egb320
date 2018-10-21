import cv2
from threading import Thread, Lock
import numpy as np
from .DetectionModel import Frame
from time import time
try:
    from picamera import PiCamera, PiResolution
    PICAMERA_MODE = True
except Exception:
    PICAMERA_MODE = False
    

PI_CAM_SENSOR_MODE = 5
PI_CAM_RESOLUTION = (1640, 922)

# Asynchronous camera / video-stream class
class VideoStream():

    def __init__(self, video_path=None, downsample_scale=1):
        self.on_disk = False
        self.piCam = None
        if video_path:
            self.frame_idx = 0
            self.cap = cv2.VideoCapture(video_path)
            self.on_disk = True
            self.resolution = (
                int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH) / downsample_scale),
                int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) / downsample_scale),
            )
        else:
            if PICAMERA_MODE:
                self.resolution = PiResolution(
                    int(PI_CAM_RESOLUTION[0] / downsample_scale),
                    int(PI_CAM_RESOLUTION[1] / downsample_scale),
                ).pad()
                self.piCam = PiCamera(sensor_mode=PI_CAM_SENSOR_MODE, resolution=self.resolution)
            else:
                self.cap = cv2.VideoCapture(0)
                self.resolution = (
                    int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH) / downsample_scale),
                    int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) / downsample_scale),
                )
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[1])
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[0])
                
            self.imageBuffer = None
            self.new_frame_lock = Lock()
            self.writing_frame_lock = Lock()
            self.started = False
            self.stopped = False



    def __iter__(self):
        return self


    def __next__(self):
        if self.on_disk:
            image = self.read_frame(self.frame_idx)
            self.frame_idx += 1
            return image
        else:
            if not self.started:
                self.start()
            self.new_frame_lock.acquire() # blocks until there is a new frame
            image = self.imageBuffer
            if self.piCam:
                image = image.reshape(self.resolution.transpose() + (3,))

        if image.shape != self.resolution + (3,):
            image = cv2.resize(image, self.resolution)

        return Frame(image)


    def update(self):
        image = None
        while True:
            if self.piCam:
                self.imageBuffer = image
                image = np.empty((self.resolution[0] * self.resolution[1] * 3,), dtype=np.uint8)
                self.piCam.capture(image, 'bgr', use_video_port=True)
                try: # hacks
                    self.new_frame_lock.release()
                except RuntimeError:
                    pass

                if self.stopped:
                    return
            else:
                _, self.imageBuffer = self.cap.read()
                try: #hacks
                    self.new_frame_lock.release()
                except RuntimeError:
                    pass
                
                if self.stopped:
                    return


    def close(self):
        self.stopped = True
        if self.piCam:
            self.piCam.close()
        else:
            self.cap.release()
            

    def read_frame(self, frame_idx):
        if not self.on_disk:
            raise Exception("Reading specific frames is not possible in a live feed... unless another feature is added")

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        _, bgr_img = self.cap.read()
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        if bgr_img.shape != self.resolution + (3,):
            bgr_img = cv2.resize(bgr_img, self.resolution)
        return Frame(bgr_img)

    
    def start(self):
        self.new_frame_lock.acquire()
        Thread(target=self.update).start()
        self.started = True