from enum import Enum
import cv2

class ColorSpace():

    def __init__(self, name, colorCvt_flag, channels):
        # name <str>
        # name of this colorspace for display purposes
        self.name = name

        # colorCvt_flag <int?>
        # flag to be used by the function cv.cvtColor() from a BGR image
        # if none, will stay as bgr image
        self.colorCvt_flag = colorCvt_flag

        # colorspace_labels <list<str>>
        # labels to be used by the pixel intensity inspector
        self.channel_labels = [label for (label, _) in channels]
        self.channel_scales = [scale for (_, scale) in channels]


    def bgr2this(self, bgr_img):
        if self.colorCvt_flag is None:
            return bgr_img
        else:
            return cv2.cvtColor(bgr_img, self.colorCvt_flag)


    def valRange(self, channel_idx):
        if self.channel_scales[channel_idx] is ColorSpaceScale.Linear:
            minVal = 0
        elif self.channel_scales[channel_idx] is ColorSpaceScale.Radial:
            minVal = -255
        
        maxVal = 255

        return minVal, maxVal



class ColorSpaceScale(Enum):

    Linear = 1
    Radial = 2



class ColorSpaces(Enum):

    BGR = ColorSpace("BGR", None, [
        ('Blue', ColorSpaceScale.Linear),
        ('Green', ColorSpaceScale.Linear),
        ('Red', ColorSpaceScale.Linear)
    ])

    HSV = ColorSpace("HSV", cv2.COLOR_BGR2HSV, [
        ('Hue', ColorSpaceScale.Radial),
        ('Saturation', ColorSpaceScale.Linear),
        ('Value', ColorSpaceScale.Linear)
    ])
    
    CIELab = ColorSpace("CIELab", cv2.COLOR_BGR2Lab, [
        ('L', ColorSpaceScale.Linear),
        ('a', ColorSpaceScale.Linear),
        ('b', ColorSpaceScale.Linear)
    ])