from .ColorSpace import ColorSpace, ColorSpaces
import cv2
import numpy as np



class Frame():
    
    def __init__(self, bgr_img):
        self.link_bgr(bgr_img)


    def get(self, colorspace=ColorSpaces.BGR):
        if type(colorspace) is ColorSpace:
            colorspace = ColorSpaces[colorspace.name]
        
        if colorspace in self.colorspace2img:
            return self.colorspace2img[colorspace]
        else:
            self.colorspace2img[colorspace] = colorspace.value.bgr2this(self.get())
            return self.colorspace2img[colorspace]


    def link_bgr(self, bgr_img):
        self.colorspace2img = {
            ColorSpaces.BGR: bgr_img
        }


    def copy_bgr(self, bgr_img):
        if bgr_img is None:
            raise "error"
        self.colorspace2img = {
            ColorSpaces.BGR: np.copy(bgr_img)
        }

    @staticmethod
    def copy_of(frame):
        this = Frame(np.array([]))
        this.copy_bgr(frame.get())
        return this