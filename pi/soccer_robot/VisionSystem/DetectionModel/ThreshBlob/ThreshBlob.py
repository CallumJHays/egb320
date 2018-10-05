from ..DetectionModel import DetectionModel
from ..DetectionResult import DetectionResult
from .Thresholder import Thresholder
import cv2
import pickle


class ThreshBlob(DetectionModel):

    def __init__(self, thresholder=None, blob_detector_params=None):

        # thresholder <Thresholder>
        # the thresholder to be applied to the image before finding blobs
        self.thresholder = thresholder or Thresholder()

        if blob_detector_params is None:
            self.blob_detector_params = cv2.SimpleBlobDetector_Params()

            self.blob_detector_params.minArea = 1
            self.blob_detector_params.maxArea = 0 # overwritten by tuner to be number of pixels in the image. ie 640 * 480
            self.blob_detector_params.minCircularity = 0.0
            self.blob_detector_params.maxCircularity = 1.0
            self.blob_detector_params.minInertiaRatio = 0.0
            self.blob_detector_params.maxInertiaRatio = 1.0
            self.blob_detector_params.minConvexity = 0.0
            self.blob_detector_params.maxConvexity = 1.0
        else:
            self.blob_detector_params = blob_detector_params
        
        self.blob_detector_params.blobColor = 255
        self.blob_detector_params.filterByInertia = True
        self.blob_detector_params.filterByConvexity = True
        self.blob_detector_params.filterByColor = True
        self.blob_detector_params.filterByArea = True
        self.blob_detector_params.filterByCircularity = True


    def apply(self, frame):
        mask = self.thresholder.apply(frame)
        blob_detector = cv2.SimpleBlobDetector_create(self.blob_detector_params)

        results = []
        for keypoint in blob_detector.detect(mask):
            x, y = keypoint.pt
            radius = keypoint.size / 2
            results.append(DetectionResult(
                coords=((int(x - radius), int(y - radius)), (int(x + radius), int(y + radius))),
                bitmask=mask
            ))

        return results

    
    # overwrite the standard pickle method because cv objects cannot be pickled (C-based structure)
    @staticmethod
    def load(path):
        data = pickle.load(open(path, 'rb'))
        
        blob_detector_params = cv2.SimpleBlobDetector_Params()
        param_names = ['Area', 'Circularity', 'InertiaRatio', 'Convexity']

        for param_name in param_names:
            setattr(blob_detector_params, 'min' + param_name, data['blob_detector_params']['min' + param_name])
            setattr(blob_detector_params, 'max' + param_name, data['blob_detector_params']['max' + param_name])

        return ThreshBlob(thresholder=data['thresholder'], blob_detector_params=blob_detector_params)

    def save(self, path):
        data = {
            'thresholder': self.thresholder,
            'blob_detector_params': {}
        }
        
        param_names = ['Area', 'Circularity', 'InertiaRatio', 'Convexity']

        for param_name in param_names:
            data['blob_detector_params']['min' + param_name] = getattr(self.blob_detector_params, 'min' + param_name)
            data['blob_detector_params']['max' + param_name] = getattr(self.blob_detector_params, 'max' + param_name)

        pickle.dump(data, open(path, 'wb'), -1)



