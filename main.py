# global imports
import os
import cv2
from time import time
from tqdm import tqdm

# subsystem imports
from VisionSystem import VisionSystem, VisualObject, VideoStream
from VisionSystem.DetectionModel import ThreshBlob
from DriveSystem import DriveSystem
from KickerSystem import KickerSystem


# Debug variables
DEBUG_MODE = True
SHOW_LIVE = False # only works in DEBUG_MODE
raw_debug_writer = None
labelled_debug_writer = None


# helper methods
def relpath(*paths):
    return os.path.join(os.path.dirname(__file__), *paths)


# load detection models and setup vision system with all objects' sizes for distance
# detection
def setup_vision_system(resolution):
    objects_to_size_and_result_limit = [
        ("ball", (0.043, 0.043, 0.043), 1),
        ("obstacle", (0.18, 0.18, 0.2), None),
        # ("blue_goal", (0.3, 0.3, 0.1), 1), # 30 centimetres long, 10 cm high? i guess
        # ("yellow_goal", (0.3, 0.3, 0.1), 1)
    ]

    return VisionSystem(camera_pixel_width=resolution[0], objects_to_track={
        name: VisualObject(
            real_size=size,
            detection_model=ThreshBlob.load(relpath("detection_models", name + "_model.threshblob.pkl")),
            result_limit=result_limit
        ) for name, size, result_limit in objects_to_size_and_result_limit
    })


def setup_debug_tools(resolution):
    index = ''
    filename = lambda: relpath('debug_data', 'profile_vid' + index)
    progress_bar = tqdm()

    while True:
        if os.path.isfile(filename() + '_raw.avi'):
            if index:
                index = '('+str(int(index[1:-1])+1)+')' # Append 1 to number in brackets
            else:
                index = '(1)'
            pass # Go and try create file again
        else:
            break

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    raw_debug_writer = cv2.VideoWriter(filename() + "_raw.avi", fourcc, 20.0, resolution)
    labelled_debug_writer = cv2.VideoWriter(filename() + '_labelled.avi', fourcc, 20.0, resolution)
    return (raw_debug_writer, labelled_debug_writer, progress_bar)


def cleanup_debug_tools(debug_tools):
    if DEBUG_MODE:
        (raw_debug_writer, labelled_debug_writer, _) = debug_tools
        raw_debug_writer.release()
        labelled_debug_writer.release()
        if SHOW_LIVE:
            cv2.destroyAllWindows()


def mainloop(vision_system, video_stream, nav_system, drive_system, kicker_system, debug_tools=None):
    if DEBUG_MODE:
        (raw_debug_writer, labelled_debug_writer, progress_bar) = debug_tools
        progress_bar = setup_debug_tools(video_stream.resolution)
        frames_this_sec = 0
        last_sec_fps = 0
        last_sec_time = time()

    while True:
        frame = next(video_stream)
        vision_system.update_with_frame(frame)
        nav_system.update()
        

        if DEBUG_MODE:
            # update fps
            raw_debug_writer.write(frame.get())
            frames_this_sec += 1
            now_time = time()

            if now_time - last_sec_time >= 1:
                last_sec_time = now_time
                last_sec_fps = frames_this_sec
                frames_this_sec = 0

            # label image with bounding boxes and fps
            vision_system.label_frame(frame)
            frame.link_bgr(cv2.putText(
                frame.get(),
                text="FPS: %d" % last_sec_fps,
                org=(15, 15),
                fontFace=cv2.FONT_HERSHEY_PLAIN,
                fontScale=1.5,
                color=(0, 255, 255)
            ))

            labelled_debug_writer.write(frame.get())

            progress_bar.update()

            if SHOW_LIVE:
                cv2.imshow('ROBOVISION', frame.get())
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break


if __name__ == '__main__':
    video_stream = VideoStream(downsample_scale=8)
    vision_system = setup_vision_system(video_stream.resolution)
    drive_system = DriveSystem(speed_modifier=0.5)
    kicker_system = KickerSystem()

    if DEBUG_MODE:
        debug_toools = setup_debug_tools(video_stream.resolution)
    else:
        debug_tools = None
        
    print("Beginning mainloop!")

    try:
        mainloop(vision_system, video_stream, drive_system, kicker_system, debug_tools)
    except KeyboardInterrupt:
        print("interrupt received, packing up...")
    finally:
        video_stream.close()
        cleanup_debug_tools()
        cv2.destroyAllWindows()
        print("All done!")