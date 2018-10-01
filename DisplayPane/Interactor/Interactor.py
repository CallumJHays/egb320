from abc import ABC, abstractmethod



class Interactor(ABC):
    # for auto-layout purposes, whether the ipy_controls of this
    # interactor should be moved to the side at smaller display pane sizes,
    # or whether it should remain underneath the display pane (as a toolbar)
    is_panel = False


    def link_with(self, display_pane):
        self.display_pane = display_pane # DisplayPane reference
        self.image_plot_marks = [] # the mark to be drawn by the DisplayPane
        self.ipy_controls = None # the IPython controls to be displayed underneath the DisplayPane
        self.observer_cbs = [] # what other components may be observing this interactor


    def set_image_plot_marks(self, image_plot_marks):
        self.image_plot_marks = image_plot_marks


    def observe(self, cb):
        self.observer_cbs.append(cb)


    def update_observers(self):
        for cb in self.observer_cbs:
            cb()