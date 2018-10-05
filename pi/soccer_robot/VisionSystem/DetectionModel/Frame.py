from .ColorSpace import ColorSpaces
import cv2
import numpy as np



class Frame():
    
    def __init__(self, bgr_img):
        self.link_bgr(bgr_img)


    def get(self, colorspace):
        if colorspace in self.colorspace2img:
            return self.colorspace2img[colorspace]
        else:
            self.colorspace2img[colorspace] = colorspace.bgr2this(self.colorspace2img[ColorSpaces.BGR])
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
        this.copy_bgr(frame.get(ColorSpaces.BGR))
        return this