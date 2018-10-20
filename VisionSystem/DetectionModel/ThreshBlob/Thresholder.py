import cv2
from ..Frame import Frame
from ..ColorSpace import ColorSpace, ColorSpaces, ColorSpaceScale
import numpy as np
from copy import copy


class Thresholder():

    def __init__(self, colorspace=ColorSpaces.BGR, lower=None, upper=None, erosion1=0, dilation1=0, erosion2=0, dilation2=0):
        # colorspace <ColorSpace>
        # the colorspace in which the threshold resides
        if colorspace in ColorSpaces:
            self.colorspace = colorspace.value
        elif type(colorspace) is ColorSpace:
            self.colorspace = colorspace
        else:
            raise Exception("colorspace must be either a ColorSpace object, or a variant of the ColorSpaces Enum")

        # lower list<int>
        # the lower bound of the accepted threshold range. Typically a 1x3 np.array
        # (depends on the color space)
        self.lower = lower or [0, 0, 0]
        
        # lower list<int>
        # the upper bound of the accepted threshold range. Typically a 1x3 np.array
        # (depends on the color space)
        self.upper = upper or [255, 255, 255]

        self.dilation1 = dilation1
        self.erosion1 = erosion1
        self.dilation2 = dilation2
        self.erosion2 = erosion2


    def apply(self, frame):
        if type(frame) is Frame:
            colorspace_img = frame.get(self.colorspace)
        else:
            colorspace_img = frame

        has_radial = any([lower < 0 for (lower, _) in self.colorspace.channel_limits])
        has_negative_val = False # until proven true, only possible if there is a radial val    

        if has_radial:
            lowers = [copy(self.lower), copy(self.lower)]
            uppers = [copy(self.upper), copy(self.upper)]
            
            for idx, (lowerVal, upperVal) in enumerate(zip(self.lower, self.upper)):
                _, maxVal = self.colorspace.valRange(idx)
                if lowerVal < 0:
                    lowers[0][idx] = 0
                    lowers[1][idx] = maxVal + lowerVal
                    has_negative_val = True
                    if upperVal < 0:
                        uppers[1][idx] = maxVal + upperVal
                    else:
                        uppers[1][idx] = maxVal

        if has_negative_val:
            mask = cv2.bitwise_or(
                cv2.inRange(colorspace_img, np.array(lowers[0], dtype=np.uint8), np.array(uppers[0], dtype=np.uint8)),
                cv2.inRange(colorspace_img, np.array(lowers[1], dtype=np.uint8), np.array(uppers[1], dtype=np.uint8))
            )
        else:
            mask = cv2.inRange(colorspace_img, np.array(self.lower, dtype=np.uint8), np.array(self.upper, dtype=np.uint8))

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        if self.dilation1 > 0:
            mask = cv2.dilate(mask, kernel, iterations=self.dilation1)
        if self.erosion1 > 0:
            mask = cv2.erode(mask, kernel, iterations=self.erosion1)
        if self.dilation2 > 0:
            mask = cv2.dilate(mask, kernel, iterations=self.dilation2)
        if self.erosion2 > 0:
            mask = cv2.erode(mask, kernel, iterations=self.erosion2)
        return mask


    def update(self, channel_idx, new_range):
        self.lower[channel_idx], self.upper[channel_idx] = new_range