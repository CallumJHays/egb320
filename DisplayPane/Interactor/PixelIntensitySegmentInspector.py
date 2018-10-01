from .Interactor import Interactor
from .SegmentSelector import SegmentSelector
import ipywidgets as ipy
import bqplot as bq
import numpy as np



class PixelIntensitySegmentInspector(Interactor):

    is_panel = True


    def __init__(self):
        self.segment_selector = SegmentSelector()


    def link_with(self, display_pane):
        super().link_with(display_pane)
        self.segment_selector.link_with(display_pane)
        self.segment_selector.observe(self.update_pixel_intensities_mark)
        self.display_pane.bq_img.observe(lambda _change: self.update_pixel_intensities_mark())

        self.ipy_controls = ipy.VBox([
            self.segment_selector.ipy_controls,
            self.make_pixel_intensities_pane()
        ])

        super().set_image_plot_marks(self.segment_selector.image_plot_marks)


    def make_pixel_intensities_pane(self):
        FULL_HEIGHT = 800

        scales = {
            'x': bq.LinearScale(min=0),
            'y': bq.LinearScale(min=0, max=255)
        }

        self.pixel_intensities_mark = bq.Lines(
            scales=scales,
            colors=['blue', 'green', 'red'],
            display_legend=True,
            opacities=[0.7] * 3
        )

        axes = [
            bq.Axis(scale=scales['y'], orientation='vertical')
        ]

        self.pixel_intensities_fig = bq.Figure(marks=[self.pixel_intensities_mark], axes=axes)
        self.pixel_intensities_fig.layout.width = '100%'
        self.pixel_intensities_fig.layout.height = str(self.display_pane.size * FULL_HEIGHT) + 'px'
        self.pixel_intensities_fig.layout.margin = '0'
        self.pixel_intensities_fig.title = 'Pixel Intensities Along Segment'
        
        self.update_pixel_intensities_mark()

        return ipy.VBox([
            self.pixel_intensities_fig,
            bq.toolbar.Toolbar(figure=self.pixel_intensities_fig)
        ])


    def update_pixel_intensities_mark(self):
        if len(self.segment_selector.segment_mark.y) == 2:

            img = self.display_pane.filtered_img
            height, width, _ = img.shape

            ys = []
            
            [init_x, final_x] = (self.segment_selector.segment_mark.x * width).astype(int)
            init_x = max(init_x, 0)
            final_x = min(final_x, width)
            
            [init_y, final_y] = (self.segment_selector.segment_mark.y * height).astype(int)
            init_y = max(init_y, 0)
            final_y = min(final_y, height)
            
            gradient = (final_y - init_y) / (final_x - init_x)
            direction = int(gradient / abs(gradient))
            curr_y = init_y
            
            for x in range(init_x, final_x):
                next_y = init_y + int(gradient * (x - init_x))

                # TODO: this can probably be more efficient but I CBF rn:
                for y in range(curr_y, next_y + direction, direction):
                    ys.append(img[height - y - 1, x])
                    
                curr_y = next_y
    
            y_arr = np.array(ys)
            self.pixel_intensities_mark.y = y_arr.T
            
            length = y_arr.shape[0]
            self.pixel_intensities_mark.x = np.repeat(
                np.arange(0, length).reshape((1, -1)),
                repeats=3, axis=0)