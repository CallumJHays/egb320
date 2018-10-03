import math



class VisualObject():

    # camera is 62.2 degrees wide
    CAMERA_FOV = 62.2 * math.pi / 180
    CAMERA_PIXEL_WIDTH = 640

    
    def __init__(self, real_size=(0, 0, 0),  detection_model=None, result_limit=None):
        # real_size <tupe<float, float, float>>
        # real size of object needing detection in metres
        self.real_size = real_size
        
        # detection_model <DetectionModel>
        # the model to be used by the vision system for detection of this object
        self.detection_model = detection_model
        
        # bearings_distances <[tuple<float, float>]>
        # the bearings, and distances respectively of the detected objects
        # in radians estimated from the camera's center of translation (for convenience),
        # with the center of vision located at pi radians.
        # listed in order of likelihood to be the correct object
        self.bearings_distances = []
        
        # detection_results <[DetectionResult]>
        # the raw detection results that were returned from the model
        self.detection_results = []

        self.result_limit=None

        
    def update_with_frame(self, frame):
        self.detection_results = self.detection_model.apply(frame)[0:self.result_limit]
        self.bearings_distances = []

        if self.detection_results:
            result = self.detection_results[0]
            bearing = (result.coords[0][0] + result.coords[1][0]) / 2
            pixel_height = result.coords[1][1] - result.coords[0][1]

            distance = 1 / pixel_height

            self.bearings_distances.append((bearing, distance))
        
        return self.detection_results