from .Interactor import Interactor
import ipywidgets as ipy
from VisionSystem.DetectionModel.ColorSpace import ColorSpaces

class ColorSpacePicker(Interactor):

    def __init__(self, colorspace=ColorSpaces.BGR.value, apply_before_custom_filter=True):
        # whether to apply the colorspace change before or after
        # any custom filter defined as `filter_fn` in DisplayPane
        # if false and `filter_fn` is defined, will provide the image
        # in the chosen colorspace when calling `filter_fn`
        # note that colourpace changes assume that the image will be in bgr
        # format when doing so
        self.apply_before_custom_filter = apply_before_custom_filter

        self.colorspace = colorspace


    def link_with(self, display_pane):
        super().link_with(display_pane)
        self.ipy_controls = ipy.Dropdown(
            description='ColorSpace: ',
            options=[colorspace.name for colorspace in ColorSpaces],
            value=self.colorspace.name
        )

        def on_change(change):
            self.colorspace = ColorSpaces[change['new']].value
            self.display_pane.display_colorspace = self.colorspace
            self.display_pane.update_data_and_display()
            self.update_observers()

        self.ipy_controls.observe(on_change, 'value')
        on_change({'new': self.colorspace.name})