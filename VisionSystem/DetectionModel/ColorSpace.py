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
        self.channel_limits = [limits for (_, limits) in channels]


    def bgr2this(self, bgr_img):
        if self.colorCvt_flag is None:
            return bgr_img
        else:
            return cv2.cvtColor(bgr_img, self.colorCvt_flag)


    def valRange(self, channel_idx):
        return self.channel_limits[channel_idx]



class ColorSpaceScale(Enum):

    Linear = 1
    Radial = 2



class ColorSpaces(Enum):

    BGR = ColorSpace("BGR", None, [
        ('Blue', (0, 255)),
        ('Green', (0, 255)),
        ('Red', (0, 255))
    ])

    HSV = ColorSpace("HSV", cv2.COLOR_BGR2HSV, [
        ('Hue', (-180, 180)),
        ('Saturation', (0, 255)),
        ('Value', (0, 255))
    ])
    
    CIELab = ColorSpace("CIELab", cv2.COLOR_BGR2Lab, [
        ('L', (0, 255)),
        ('a', (0, 255)),
        ('b', (0, 255))
    ])