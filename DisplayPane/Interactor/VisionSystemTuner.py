import ipywidgets as ipy
from .Interactor import Interactor
from .DetectionModelTuner import DetectionModelTuner


class VisionSystemTuner(Interactor):

    is_panel = True
    

    def __init__(self, vision_system):
        self.vision_system = vision_system
    

    def link_with(self, display_pane):
        super().link_with(display_pane)

        tuners = []

        for _, obj in self.vision_system.objects_to_track.items():
            tuner = DetectionModelTuner(obj.detection_model)
            tuner.link_with(display_pane)
            tuner.model_display.hide()
            tuners.append(tuner)

        tuners[0].model_display.show()

        self.ipy_controls = ipy.Accordion(children=[tuner.ipy_controls for tuner in tuners])

        def on_change(change):
            if change['old'] is not None:
                tuners[change['old']].model_display.hide()
                
            if change['new'] is not None:
                tuners[change['new']].model_display.show()

        self.ipy_controls.observe(on_change, 'selected_index')
        
        # name them after their assigned names
        for idx, (name, _) in enumerate(self.vision_system.objects_to_track.items()):
            self.ipy_controls.set_title(idx, name)