from .Interactor import Interactor
import cv2
import ipywidgets as ipy

##############
# DOES NOT WORK!!!!! Need to add to the js in bqplot/js/Marks/Image

class MaskSelector(Interactor):

    def __init__(self, mask=None, selector_kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))):
        
        self.mask = mask
        self.bq_selection_outline = None
        self.selector_indicator = None
        self.selector_kernel = selector_kernel

    
    def link_with(self, display_pane):
        super().link_with(display_pane)

        self.ipy_controls = self.make_mask_paint_selector()
        display_pane.image_plot.on_hover(lambda c: print('hover', c))
        display_pane.image_plot.observe(lambda c: print('observe', c))
        display_pane.image_plot.on_msg(lambda c: print('msg', c))
        print(dir(display_pane.image_plot))


    def make_mask_paint_selector(self):


        
        return ipy.HBox([])