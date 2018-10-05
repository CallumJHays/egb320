import cv2
from ..Frame import Frame
from ..ColorSpace import ColorSpace, ColorSpaces



class Thresholder():

    def __init__(self, colorspace=ColorSpaces.BGR.value, lower=None, upper=None):
        # colorspace <ColorSpace>
        # the colorspace in which the threshold resides
        print(colorspace)
        if colorspace in ColorSpaces:
            self.colorspace = colorspace.value
        elif type(colorspace) is ColorSpace:
            self.colorspace = colorspace
        else:
            raise Exception("colorspace must be either a ColorSpace object, or a variant of the ColorSpaces Enum")

        # lower list<int>
        # the lower bound of the accepted threshold range. Typically a 1x3 np.array
        # (depends on the color space)
        self.lower = lower or (0, 0, 0)
        
        # lower list<int>
        # the upper bound of the accepted threshold range. Typically a 1x3 np.array
        # (depends on the color space)
        self.upper = upper or (255, 255, 255)


    def apply(self, frame):
        if type(frame) is Frame:
            colorspace_img = frame.get(self.colorspace)
        else:
            colorspace_img = frame

        return cv2.inRange(colorspace_img, self.lower, self.upper)


    def update(self, channel_idx, new_range):
        lower_list = list(self.lower)
        upper_list = list(self.upper)
        lower_list[channel_idx], upper_list[channel_idx] = new_range
        self.lower = tuple(lower_list)
        self.upper = tuple(upper_list)