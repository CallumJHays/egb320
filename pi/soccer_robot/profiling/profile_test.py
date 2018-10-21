from tqdm import tqdm
import os, sys
import numpy as np
import cv2
from time import time

SHOW_VIDEO = False

def relpath(*paths):
    return os.path.join(os.path.dirname(__file__), *paths)
    

def load_or_create_new_threshblob(path):
    try:
        model = ThreshBlob.load(path)
        print("Loaded " + path)
    except Exception:
        model = ThreshBlob()
    finally:
        return model

PROFILE_VIDEO = "init_test_6pm.mp4"
index = ''
video_path = relpath("..", "data", PROFILE_VIDEO)

RPI_MODE = os.path.exists(video_path)
if RPI_MODE: # on rpi
    profile_data_filepath = lambda more: relpath('profile_data', more)
    sys.path.append(relpath(".."))
else: # on desktop
    video_path = relpath("..", "..", "data", PROFILE_VIDEO)
    profile_data_filepath = lambda more: relpath('..', '..', 'profile_data', more)
    sys.path.append(relpath("..", "..", ".."))

filepath = lambda: profile_data_filepath('profile_vid' + index + '.avi')

from VisionSystem import VisionSystem, VisualObject, VideoStream
from VisionSystem.DetectionModel import ThreshBlob, Frame, ColorSpaces


model_names = ["ball", "obstacle", "yellow_goal", "blue_goal", "free_ground_space"]
if RPI_MODE:
    detection_models = {
        model_name: load_or_create_new_threshblob(relpath("..", "detection_models",  model_name + "_model.threshblob.pkl")) \
                        for model_name in model_names
    }
else:
    detection_models = {
        model_name: load_or_create_new_threshblob(relpath("..", "..", "..", "detection_models",  model_name + "_model.threshblob.pkl")) \
                        for model_name in model_names
    }

objects_to_track = {
    name: VisualObject(real_size=(0.043, 0.043, 0.043), detection_model=model)
            for name, model in detection_models.items()
}

vision_system = VisionSystem(objects_to_track)


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

cam = VideoStream(downsample_scale=8)
raw_writer = cv2.VideoWriter(filepath() + "_raw.avi", fourcc, 20.0, cam.resolution)
labelled_writer = cv2.VideoWriter(filepath(), fourcc, 20.0, cam.resolution)

frames_this_sec = 0
last_sec_fps = 0
last_sec_time = time()
last_frame = 100
frame_idx = 0
pbar = tqdm(total=last_frame)

try:
    for frame in cam:
        raw_writer.write(frame.get())
        vision_system.update_with_and_label_frame(frame)
        frames_this_sec += 1
        now_time = time()

        if now_time - last_sec_time >= 1:
            last_sec_time = now_time
            last_sec_fps = frames_this_sec
            frames_this_sec = 0

        frame.link_bgr(cv2.putText(
            frame.get(),
            text="FPS: %d" % last_sec_fps,
            org=(15, 15),
            fontFace=cv2.FONT_HERSHEY_PLAIN,
            fontScale=1.5,
            color=(0, 255, 255)
        ))

        labelled_writer.write(frame.get())
        frame_idx += 1
        pbar.update(1)

        if SHOW_VIDEO:
            cv2.imshow('frame', frame.get())
            if cv2.waitKey(33) & 0xFF == ord('q'):
                break

        if frame_idx > last_frame:
            break

except KeyboardInterrupt:
    print("interrupt received, packing up...")

# Release everything if job is finished
cam.close()
raw_writer.release()
labelled_writer.release()
cv2.destroyAllWindows()
print("All done!")