from ..Interactor import Interactor
from abc import ABC, abstractmethod



class DetectionModelTunerABC(Interactor, ABC):
    
    is_panel = True # all of these tuners should be treated as panels
    

    def __init__(self, detection_model):
        self.detection_model = detection_model


    def link_with(self, display_pane):
        super().link_with(display_pane)
        self.ipy_controls = self.make_ipy_controls()


    @abstractmethod
    def make_ipy_controls(self):
        pass