from ..DetectionModel import DetectionModel
from ..DetectionResult import DetectionResult
from .Thresholder import Thresholder
import cv2
import pickle
import numpy as np


class ThreshBlob(DetectionModel):

    def __init__(self, thresholder=None, blob_detector_params=None):

        # thresholder <Thresholder>
        # the thresholder to be applied to the image before finding blobs
        self.thresholder = thresholder or Thresholder()

        if blob_detector_params is None:
            self.blob_detector_params = {}

            self.blob_detector_params["minArea"] = 1
            self.blob_detector_params["maxArea"] = 0 # overwritten by tuner to be number of pixels in the image. ie 640 * 480
            self.blob_detector_params["minCircularity"] = 0.0
            self.blob_detector_params["maxCircularity"] = 1.0
            self.blob_detector_params["minInertiaRatio"] = 0.0
            self.blob_detector_params["maxInertiaRatio"] = 1.0
            self.blob_detector_params["minConvexity"] = 0.0
            self.blob_detector_params["maxConvexity"] = 1.0
        else:
            self.blob_detector_params = blob_detector_params
        
        self.blob_detector_params["blobColor"] = 255
        self.blob_detector_params["filterByInertia"] = True
        self.blob_detector_params["filterByConvexity"] = True
        self.blob_detector_params["filterByColor"] = True
        self.blob_detector_params["filterByArea"] = True
        self.blob_detector_params["filterByCircularity"] = True


    def apply(self, frame):
        mask = self.thresholder.apply(frame)
        height, width = mask.shape
        params = cv2.SimpleBlobDetector_Params()
        for name, val in self.blob_detector_params.items():
            setattr(params, name, val)
        blob_detector = cv2.SimpleBlobDetector_create(params)

        results = []
        for keypoint in blob_detector.detect(mask):
            x, y = keypoint.pt
            x, y = int(x), int(y)

            # detect contours to find the true bounding rect
            contour_padding = int(keypoint.size * 0.75)
            roi = (
                (max(y - contour_padding, 0), min(y + contour_padding, height)),
                (max(x - contour_padding, 0), min(x + contour_padding, width))
            )
            _, contours, _ = cv2.findContours(
                mask[roi[0][0]:roi[0][1], roi[1][0]:roi[1][1]].copy(),
                cv2.RETR_TREE,
                cv2.CHAIN_APPROX_SIMPLE
            )

            (x1, y1), (x2, y2) = find_bounding_box(contours)

            # restore the offsets invoked by ROI-based contour detection
            x1 += roi[1][0]
            x2 += roi[1][0]
            y1 += roi[0][0]
            y2 += roi[0][0]

            results.append(DetectionResult(
                coords=((x1, y1), (x2, y2)),
                bitmask=mask
            ))

        return results



def find_bounding_box(contours):
    # find the rectangle that includes all points in the contour
    x1, y1 = 99999999, 999999999
    x2, y2 = -99999999, -999999999

    for contour in contours:
        for [[cx, cy]] in contour:
            if x1 > cx:
                x1 = cx
            elif x2 < cx:
                x2 = cx
            
            if y1 > cy:
                y1 = cy
            elif y2 < cy:
                y2 = cy

    return (x1, y1), (x2, y2)