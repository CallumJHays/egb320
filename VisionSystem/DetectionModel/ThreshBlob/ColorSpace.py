from enum import Enum
import cv2



class ColorSpace():

    def __init__(self, name, colorCvt_flag, channel_labels):
        # name <str>
        # name of this colorspace for display purposes
        self.name = name

        # colorCvt_flag <int?>
        # flag to be used by the function cv.cvtColor() from a BGR image
        # if none, will stay as bgr image
        self.colorCvt_flag = colorCvt_flag

        # colorspace_labels <list<str>>
        # labels to be used by the pixel intensity inspector
        self.channel_labels = channel_labels


    def bgr2this(self, bgr_img):
        if self.colorCvt_flag is None:
            return bgr_img
        else:
            return cv2.cvtColor(bgr_img, self.colorCvt_flag)



class ColorSpaces(Enum):

    RGB = ColorSpace("RGB", None, ['Blue', 'Green', 'Red'])
    HSV = ColorSpace("HSV", cv2.COLOR_BGR2HSV, ['Hue', 'Saturation', 'Value'])
    CIELab = ColorSpace("CIELab", cv2.COLOR_BGR2Lab, ['L', 'a', 'b'])