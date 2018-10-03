from .ThreshBlobTuner import ThreshBlobTuner
from enum import Enum
        

class DetectionModelTuners(Enum):
    
    ThreshBlob = ThreshBlobTuner
    

# fake class used to make using above more fluid
def DetectionModelTuner(detection_model):
    tuner_class = DetectionModelTuners[detection_model.__class__.__name__].value
    return tuner_class(detection_model)
