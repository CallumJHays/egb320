import cv2
import numpy as np
import math


class VisionSystem():

    CATEGORICAL_COLORS = [
        (211, 47, 47), # red
        (25, 118, 210), # blue
        (56, 142, 60), # green
        (251, 192, 45), # yellow
        (69, 90, 100), # bluegray
        (194, 24, 91), # pink
        (123, 31, 162), # purple
        (230, 74, 25), # orange
        (0, 121, 107) # teal
    ]


    def __init__(self, objects_to_track={}):
        # objects_to_track <dict<key=str, val=VisualObject>>
        # the objects that the vision system should attempt to track every time
        # update_with_frame() is called
        self.objects_to_track = objects_to_track
        

    def update_with_frame(self, frame):
        return {
            key: obj.update_with_frame(frame)
                for key, obj in self.objects_to_track.items()
        }


    def update_with_and_label_frame(self, frame):
        self.update_with_frame(frame)
        self.label_frame(frame)

        
    def label_frame(self, frame):
        for obj_idx, (name, obj_type) in enumerate(self.objects_to_track.items()):
            for res_idx, (result, (bearing, distance)) in enumerate(zip(obj_type.detection_results, obj_type.bearings_distances)):
                draw_color = VisionSystem.CATEGORICAL_COLORS[obj_idx]
                frame = cv2.rectangle(frame, result.coords[0], result.coords[1], draw_color)

                frame = cv2.putText(
                    frame,
                    text="%s%d: %.2fcm@%.0fdeg" % (name, res_idx, distance * 100, bearing * 180 / math.pi),
                    org=(result.coords[0][0], result.coords[0][1] - 10),
                    fontFace=cv2.FONT_HERSHEY_PLAIN,
                    fontScale=1,
                    color=draw_color
                )
