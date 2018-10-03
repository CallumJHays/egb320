from .Interactor import Interactor
import bqplot as bq
import ipywidgets as ipy

class SegmentSelector(Interactor):
    


    def __init__(self, title="Segment Selector: "):
        # mark to draw over the image plot also used to
        # define the bounding box for which the segment is defined
        self.segment_mark = None 
        self.segment_drawer = None # segment drawing interactor
        # upon which diagonal to draw the segment
        # within the selected bounding box
        self.segment_draw_diagonal = False
        self.title = title


    def link_with(self, display_pane):
        super().link_with(display_pane)
        
        self.segment_mark, self.segment_drawer = self.make_segment_mark_and_drawer()

        self.ipy_controls = ipy.HBox([
            ipy.Label(self.title),
            self.make_segment_draw_mode_toggler(),
            self.make_segment_draw_diag_switch()
        ])
        
        super().set_image_plot_marks([self.segment_mark])


    def make_segment_mark_and_drawer(self):
        mark = bq.Lines(
            scales=self.display_pane.image_plot_scales,
            x=[0.45, 0.55],
            y=[0.45, 0.55]
        )

        drawer = bq.interacts.BrushSelector(
            x_scale=self.display_pane.image_plot_scales['x'],
            y_scale=self.display_pane.image_plot_scales['y'],
            color='blue'
        )

        def on_interaction(change):
            if change['name'] == 'selected_x':
                mark.x = change['new']
            elif change['name'] == 'selected_y':
                if self.segment_draw_diagonal:
                    mark.y = list(reversed(change['new']))
                else:
                    mark.y = change['new']
            self.update_observers()

        drawer.observe(on_interaction, ['selected_x', 'selected_y'])

        return mark, drawer
        

    def make_segment_draw_mode_toggler(self):
        togglebutton = ipy.ToggleButton(
            value=False,
            tooltip='Edit Segment Selector',
            icon='edit'
        )

        def on_toggle(change):
            if change['new']:
                self.display_pane.set_interaction(self.segment_drawer)
            else:
                self.display_pane.clear_interaction()

        togglebutton.observe(on_toggle, 'value')
        self.display_pane.add_to_togglebutton_group(togglebutton)
        return togglebutton


    def make_segment_draw_diag_switch(self):
        button = ipy.Button(
            value=False,
            icon='arrows-h',
            tooltip='Swap Segment Selector Direction'
        )

        def handle_click(_change):
            self.segment_draw_diagonal = not self.segment_draw_diagonal
            self.segment_mark.y = list(reversed(self.segment_mark.y))
            self.update_observers()

        button.on_click(handle_click)
        
        return button
