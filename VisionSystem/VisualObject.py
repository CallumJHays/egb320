class VisualObject():
    
    def __init__(self, real_size=(0, 0, 0),  detection_model=None):
        # real_size <tupe<float, float, float>>
        # real size of object needing detection in metres
        self.real_size = real_size
        
        # detection_model <DetectionModel>
        # the model to be used by the vision system for detection of this object
        self.detection_model = detection_model
        
        # bearings <[float]>
        # in radians estimated from the camera's center of translation (for convenience),
        # with the center of vision located at pi radians.
        # listed in order of likelihood to be the correct object
        self.estimated_bearings = None
        
        # distances <[float]>
        # estimated distance of obects in the last frame processed (in metres)
        # listed in order of likelihood to be the correct object
        self.estimated_distances = None
        
    def update_with_frame(self, frame):
        keypoints = self.detection_model.apply(frame)
        return keypoints