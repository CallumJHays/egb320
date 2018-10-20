import cv2
from multiprocessing import Process, Queue
import numpy as np
from .DetectionModel import Frame
try:
    from picamera import PiCamera
    PICAMERA_MODE = True
except Exception:
    PICAMERA_MODE = False

PI_CAM_SENSOR_MODE = 5
PI_CAM_RESOLUTION = (1640, 922)

# Asynchronous camera / video-stream class
class VideoStream():

    def __init__(self, video_path=None, downsample_scale=1):
        using_pi_camera = False
        self.on_disk = False
        if video_path:
            self.frame_idx = 0
            self.cap = cv2.VideoCapture(video_path)
            self.on_disk = True
            self.resolution = (
                int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH) / downsample_scale),
                int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) / downsample_scale),
            )
        else:
            self.img_queue = Queue(1)
            self.poller = Process(target=poll_video_source, args=(self.img_queue, using_pi_camera, downsample_scale))
            self.poller.start()
            self.resolution = self.img_queue.get()
            self.curr_frame = Frame(self.img_queue.get())



    def __iter__(self):
        return self


    def __next__(self):
        if self.on_disk:
            image = self.read_frame(self.frame_idx)
            self.frame_idx += 1
            return image
        else:
            image =  self.img_queue.get()

        if image.shape != self.resolution + (3,):
            image = cv2.resize(image, self.resolution)

        return Frame(image)


    def read_frame(self, frame_idx):
        if not self.on_disk:
            raise Exception("Reading specific frames is not possible in a live feed... unless another feature is added")

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        _, bgr_img = self.cap.read()
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        if bgr_img.shape != self.resolution + (3,):
            bgr_img = cv2.resize(bgr_img, self.resolution)
        return Frame(bgr_img)


    def __enter__(self):
        return self


    def __exit__(self, _exc_type, _exc_val, _traceback):
        self.close()


    def close(self):
        # TODO PROPERLY, CLOSE FILE IN OTHER PIPE VIA DUPLEX COMMINICATION
        self.poller.terminate()



def poll_video_source(img_queue, using_pi_camera, downsample_scale):
    if using_pi_camera:
        res = (int(PI_CAM_RESOLUTION[0] / downsample_scale), int(PI_CAM_RESOLUTION[1] / downsample_scale))
        cap = PiCamera(sensor_mode=PI_CAM_SENSOR_MODE)
        using_pi_camera = True
    else:
        cap = cv2.VideoCapture(0)
        res = (
            int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) / downsample_scale),
            int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) / downsample_scale),
        )
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, res[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, res[1])

    # send back the resolution for the bits and pieces
    img_queue.put(res)

    # and start collecting and keeping the queue updated with the latest frame
    while(True):
        if using_pi_camera:
            image = np.empty((PI_CAM_RESOLUTION[0] * PI_CAM_RESOLUTION[1] * 3,), dtype=np.uint8)
            cap.capture(image, 'bgr')
            image = image.reshape(PI_CAM_RESOLUTION + (3,))
        else:
            _, image = cap.read()
        
        # remove any frame on the queue if there is one
        try:
            img_queue.get_nowait()
        except Exception:
            pass
        img_queue.put_nowait(image)