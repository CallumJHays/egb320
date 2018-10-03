import bqplot as bq
import ipywidgets as ipy
import cv2
import numpy as np



class DisplayPane(ipy.VBox):

    FULL_EXTERNAL_WIDTH = 983
    FULL_INTERNAL_WIDTH = 745
    FULL_OFFSET = 240

    def __init__(self, camera=None, path=None, img=None, is_video=False, interactors=None, size=None, vision_system=None, \
            filter_fn=None, apply_filter_to_vision_system_input=False, update_frame_cbs=None, **kwargs):

        if not (path is None) ^ (img is None):
            raise Exception("either path or img must be defined, and not both")
        
        self.bq_img = None
        self.raw_img = None
        self.video_capture = None # until potentially overwritten
        self.size = size or 1
        self.togglebutton_group = []
        self.interactors = interactors or []
        self.vision_system = vision_system
        self.filter_fn = filter_fn
        self.apply_filter_to_vision_system_input = apply_filter_to_vision_system_input
        self.image_plot_scales = {'x': bq.LinearScale(), 'y': bq.LinearScale()}
        self.update_frame_cbs = update_frame_cbs or []
        
        # read the data from a file to display
        if img is None:
            if is_video:
                self.setup_video(path)
            elif camera is not None:
                self.setup_video(camera)
            else:
                self.raw_img = cv2.imread(path)
        else:
            self.raw_img = img

        self.filtered_img = np.zeros(self.raw_img.shape)
        self.labelled_img = np.zeros(self.raw_img.shape)

        self.update_data_and_display()

        # link all required interactors
        for interactor in self.interactors:
            interactor.link_with(self)

        self.image_plot = self.make_image_plot()

        panel_controls = [interactor.ipy_controls for interactor in self.interactors if interactor.is_panel]
        toolbar_controls = [interactor.ipy_controls for interactor in self.interactors if not interactor.is_panel]
        
        display_pane = ipy.VBox([
            self.image_plot,
            self.make_image_tools(self.image_plot)
        ] + toolbar_controls)
        display_pane.layout.width = str(self.size * self.FULL_EXTERNAL_WIDTH) + 'px'

        # fill accross 1/size times before filling downwards
        hbox_list = [display_pane]
        vbox_list = []

        for controls in panel_controls:
            hbox_list.append(controls)

            if len(hbox_list) == int(1 / size):
                vbox_list.append(ipy.HBox(hbox_list))
                hbox_list = []
        
        # add the remainder
        vbox_list += hbox_list
        
        super().__init__(vbox_list, **kwargs)


    def setup_video(self, source):
        self.video_capture = cv2.VideoCapture(source)
        if not self.video_capture.isOpened():
            raise ValueError("Video at " + source + " cannot be opened")
        self.raw_img = read_frame(self.video_capture, 0)
        

    def make_image_plot(self):

        marks = [self.bq_img]
        for interactor in self.interactors:
            marks += interactor.image_plot_marks

        image_plot = bq.Figure(
            marks=marks,
            padding_y=0
        )
        
        height, width, _ = self.raw_img.shape
        # make sure the image is displayed with the correct aspect ratio
        image_plot.layout.width = '100%'
        image_plot.layout.margin = '0'
        image_plot.layout.height = str(self.size * self.FULL_INTERNAL_WIDTH * height / width + self.size * self.FULL_OFFSET) + 'px'

        return image_plot
    

    def make_image_tools(self, image_plot):
        widget_list = [   
            self.make_toggle_panzoom_button(image_plot),
            self.make_reset_zoom_button()
        ]
        
        if self.video_capture is not None:
            widget_list.append(self.make_video_controller())

        return ipy.HBox(widget_list)
        

    def make_toggle_panzoom_button(self, image_plot):
        self.image_plot_panzoom = bq.interacts.PanZoom(
            scales={'x': [self.image_plot_scales['x']], 'y': [self.image_plot_scales['y']]},
        )

        button = ipy.ToggleButton(
            value=False,
            tooltip='Toggle Pan / Zoom',
            icon='arrows'
        )
        button.layout.width = '60px'

        def on_toggle(change):
            if change['new']:
                image_plot.interaction = self.image_plot_panzoom
            else:
                image_plot.interaction = None

        button.observe(on_toggle, 'value')
        self.add_to_togglebutton_group(button)

        return button
        

    def make_reset_zoom_button(self):
        button = ipy.Button(
            disabled=False,
            tooltip='Reset zoom',
            icon='refresh'
        )
        button.layout.width = '60px'

        def on_click(_change):
            self.image_plot_panzoom.scales['x'][0].min = None
            self.image_plot_panzoom.scales['x'][0].max = None
            self.image_plot_panzoom.scales['y'][0].min = None
            self.image_plot_panzoom.scales['y'][0].max = None

        button.on_click(on_click)

        return button
    

    def make_video_controller(self):
        last_frame = self.video_capture.get(cv2.CAP_PROP_FRAME_COUNT) - 1

        player = ipy.Play(
            interval=1000 / self.video_capture.get(cv2.CAP_PROP_FPS),
            max=last_frame
        )
        
        slider = ipy.IntSlider(max=last_frame)
        ipy.link((player, 'value'), (slider, 'value'))

        def on_framechange(change):
            frame_idx = change['new']
            self.raw_img = read_frame(self.video_capture, frame_idx)
            self.update_data_and_display()

        player.observe(on_framechange, 'value')
        slider.observe(on_framechange, 'value')

        def change_slider(amount):
            def cb(_change):
                slider.value += amount
                if slider.value > last_frame:
                    slider.value = last_frame
                elif slider.value < 0:
                    slider.value = 0
            return cb

        prev_frame_button = ipy.Button(
            icon='step-backward',
            tooltip='Previous Frame'
        )
        prev_frame_button.layout.width = '60px'
        prev_frame_button.on_click(change_slider(-1))

        next_frame_button = ipy.Button(
            icon='step-forward',
            tooltip='Next Frame'
        )
        next_frame_button.layout.width = '60px'
        next_frame_button.on_click(change_slider(+1))

        controller = ipy.HBox([prev_frame_button, player, next_frame_button, slider])
        return controller


    def update_data_and_display(self):
        # filter the image if need be
        self.filtered_img[:] = self.raw_img[:]
        if self.filter_fn is not None:
            print(self.filtered_img.shape)
            self.filter_fn(self.filtered_img)
        
        self.labelled_img[:] = self.filtered_img[:]
        if self.vision_system is not None:
            self.vision_system.update_with_and_label_frame(self.labelled_img)

        for cb in self.update_frame_cbs:
            cb()
        
        ipy_img = ipy.Image(value=cv2.imencode('.jpg', self.labelled_img)[1].tostring(), format='jpg')
        
        if self.bq_img is None:
            self.bq_img = bq.Image(image=ipy_img, scales=self.image_plot_scales)
        else:
            self.bq_img.image = ipy_img


    def link_frame(self, master_pane):

        def on_update_frame():
            self.raw_img = master_pane.raw_img
            self.update_data_and_display()

        master_pane.update_frame_cbs.append(on_update_frame)


    def add_interactor(self, display_pane_interactor):
        display_pane_interactor.link_with(self)
        self.interactors.append(display_pane_interactor)


    def set_interaction(self, interaction):
        self.image_plot.interaction = interaction


    def clear_interaction(self):
        self.image_plot.interaction = None
        

    def add_to_togglebutton_group(self, togglebutton):
        self.togglebutton_group.append(togglebutton)
                
        def on_toggle(change):
            if change['new'] is True:
                for button in self.togglebutton_group:
                    if button is not togglebutton:
                        button.value = False
                        
        togglebutton.observe(on_toggle, 'value')



def read_frame(video, frame_idx):
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
    _, frame = video.read()
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
    return frame