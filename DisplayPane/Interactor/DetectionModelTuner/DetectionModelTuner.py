from ..Interactor import Interactor
from .ThreshBlobTuner import ThreshBlobTuner
from abc import ABC, abstractmethod
from enum import Enum



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
        

class DetectionModelTuners(Enum):
    
    ThreshBlob = ThreshBlobTuner
    

# fake class used to make using above more fluid
def DetectionModelTuner(detection_model):
    tuner_class = DetectionModelTuners[detection_model.__class__.__name__].value
    return tuner_class(detection_model)
