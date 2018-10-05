from .DetectionModelTunerABC import DetectionModelTunerABC
from ..ColorSpacePicker import ColorSpacePicker
import ipywidgets as ipy
from VisionSystem import VisionSystem, VisualObject
from VisionSystem.DetectionModel import ColorSpaces
from ...DisplayPane import DisplayPane
import cv2
import math



class ThreshBlobTuner(DetectionModelTunerABC):

    def make_ipy_controls(self):
        ipy_controls = ipy.VBox([
            self.make_thresholder_controls(),
            self.make_blob_detector_controls()
        ])
        self.model_display.update_data_and_display()
        
        return ipy_controls


    def make_thresholder_controls(self):
        colorspace_picker = ColorSpacePicker(colorspace=self.detection_model.thresholder.colorspace)

        def threshold_with_color(frame):
            mask = self.detection_model.thresholder.apply(frame)
            img = frame.get(ColorSpaces.BGR)
            return cv2.bitwise_and(img, img, mask=mask)

        self.model_display = DisplayPane(
            frame=self.display_pane.raw_frame,
            size=self.display_pane.size,
            interactors=[colorspace_picker],
            filter_fn=threshold_with_color,
            vision_system=VisionSystem({ 'obj': VisualObject(detection_model=self.detection_model) })
        )
        self.model_display.link_frame(self.display_pane)
        sliders = []

        # make a slider for each channel of the thresholder
        for idx in range(len(self.detection_model.thresholder.lower)):
            
            slider = ipy.IntRangeSlider(
                description=self.detection_model.thresholder.colorspace.channel_labels[idx],
                value=(
                    self.detection_model.thresholder.lower[idx],
                    self.detection_model.thresholder.upper[idx]
                ),
                min=0,
                max=255
            )
            slider.layout.width = '95%'

            def on_change(idx):
                def update(change):
                    self.detection_model.thresholder.update(idx, change['new'])
                    self.model_display.update_data_and_display()

                return update

            slider.observe(on_change(idx), 'value')
            sliders.append(slider)

        def on_colorspace_change():
            self.detection_model.thresholder.colorspace = colorspace_picker.colorspace

            # update the descriptions
            for idx, slider in enumerate(sliders):
                slider.description = self.detection_model.thresholder.colorspace.channel_labels[idx]

        colorspace_picker.observe(on_colorspace_change)

        return ipy.VBox([self.model_display] + sliders)


    def make_blob_detector_controls(self):
        param_names = ['Area', 'Circularity', 'InertiaRatio', 'Convexity']
        sliders = []

        for param_name in param_names:
            slider_value = (
                getattr(self.detection_model.blob_detector_params, 'min' + param_name),
                getattr(self.detection_model.blob_detector_params, 'max' + param_name)
            )

            # make sure maxArea is only set to the number of pixels on the screen
            if param_name == 'Area':
                length, width, _ = self.model_display.raw_frame.get(ColorSpaces.BGR).shape
                max_exponent = math.log(length * width)
                slider_range = (1, max_exponent)
                self.detection_model.blob_detector_params.maxArea = length * width
                slider_value = (math.log(slider_value[0]), math.log(self.detection_model.blob_detector_params.maxArea))
            else:
                slider_range = (0.0, 1.0)

            def on_change(param_name):
                def update(change):
                    newMin, newMax = change['new']
                    if param_name == 'Area':
                        newMin = math.exp(newMin)
                        newMax = math.exp(newMax)
                    setattr(self.detection_model.blob_detector_params, 'min' + param_name, newMin)
                    setattr(self.detection_model.blob_detector_params, 'max' + param_name, newMax)
                    self.model_display.update_data_and_display()
                return update

            slider = ipy.FloatRangeSlider(
                description=param_name,
                min=slider_range[0],
                max=slider_range[1],
                value=slider_value,
                step=0.0001
            )
            slider.layout.width = '95%'
            slider.observe(on_change(param_name), 'value')
            
            sliders.append(slider)

        return ipy.VBox(sliders)
