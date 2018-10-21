from .DetectionModelTunerABC import DetectionModelTunerABC
from ..ColorSpacePicker import ColorSpacePicker
import ipywidgets as ipy
from VisionSystem import VisionSystem, VisualObject
from VisionSystem.DetectionModel import ColorSpaces, ColorSpaceScale
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
            vision_system=VisionSystem(
                objects_to_track={ 'obj': VisualObject(detection_model=self.detection_model) },
                camera_pixel_width=self.display_pane.video_stream.resolution[0]
            )
        )
        self.model_display.link_frame(self.display_pane)
        channel_sliders = []
        thresh = self.detection_model.thresholder

        # make a slider for each channel of the thresholder
        for idx in range(len(thresh.lower)):

            minVal, maxVal = thresh.colorspace.valRange(idx)

            slider = ipy.IntRangeSlider(
                description=thresh.colorspace.channel_labels[idx],
                value=(thresh.lower[idx], thresh.upper[idx]),
                min=minVal,
                max=maxVal
            )
            slider.layout.width = '95%'

            def on_change(idx):
                def update(change):
                    thresh.update(idx, change['new'])
                    self.model_display.update_data_and_display()

                return update

            slider.observe(on_change(idx), 'value')
            channel_sliders.append(slider)

        def on_colorspace_change():
            thresh.colorspace = colorspace_picker.colorspace

            # update the descriptions
            for idx, slider in enumerate(channel_sliders):
                slider.description = thresh.colorspace.channel_labels[idx]
                minVal, maxVal = thresh.colorspace.valRange(idx)
                slider.min = minVal
                slider.max = maxVal
            

        colorspace_picker.observe(on_colorspace_change)

        dilation1_slider = ipy.IntSlider(
            description='Dilation 1',
            value=thresh.dilation1,
            min=0,
            max=50
        )
        dilation1_slider.layout.width = '95%'

        erosion1_slider = ipy.IntSlider(
            description='Erosion 1',
            value=thresh.erosion1,
            min=0,
            max=50
        )
        erosion1_slider.layout.width = '95%'

        dilation2_slider = ipy.IntSlider(
            description='Dilation 2',
            value=thresh.dilation2,
            min=0,
            max=50
        )
        dilation2_slider.layout.width = '95%'

        erosion2_slider = ipy.IntSlider(
            description='Erosion 2',
            value=thresh.erosion2,
            min=0,
            max=50
        )
        erosion2_slider.layout.width = '95%'

        def on_change_erosion_dilation(attr):
            def update(change):
                thresh[attr] = change['new']
                self.model_display.update_data_and_display()
            return update

        dilation1_slider.observe(on_change_erosion_dilation('dilation1'), 'value')
        erosion1_slider.observe(on_change_erosion_dilation('erosion1'), 'value')
        dilation2_slider.observe(on_change_erosion_dilation('dilation2'), 'value')
        erosion2_slider.observe(on_change_erosion_dilation('erosion2'), 'value')

        return ipy.VBox([self.model_display] + channel_sliders +
            [dilation1_slider, erosion1_slider, dilation2_slider, erosion2_slider])


    def make_blob_detector_controls(self):
        param_names = ['Area', 'Circularity', 'InertiaRatio', 'Convexity']
        sliders = []

        for param_name in param_names:
            slider_value = (
                self.detection_model.blob_detector_params['min' + param_name],
                self.detection_model.blob_detector_params['max' + param_name]
            )

            # make sure maxArea is only set to the number of pixels on the screen
            if param_name == 'Area':
                length, width, _ = self.model_display.raw_frame.get(ColorSpaces.BGR).shape
                max_exponent = math.log(length * width)
                slider_range = (1, max_exponent)
                self.detection_model.blob_detector_params['maxArea'] = length * width
                slider_value = (math.log(slider_value[0]), math.log(self.detection_model.blob_detector_params['maxArea']))
            else:
                slider_range = (0.0, 1.0)

            def on_change(param_name):
                def update(change):
                    newMin, newMax = change['new']
                    if param_name == 'Area':
                        newMin = math.exp(newMin)
                        newMax = math.exp(newMax)
                    self.detection_model.blob_detector_params['min' + param_name, newMin]
                    self.detection_model.blob_detector_params['max' + param_name, newMax]
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
