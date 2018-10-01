import cv2
import numpy as np



class VisionSystem():

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
        system_keypoints = self.update_with_frame(frame)
        for keypoints in system_keypoints.values():
            frame = cv2.drawKeypoints(frame, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        return frame
        
    def label_frame(self, frame):
        return frame
