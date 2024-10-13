from PySide6 import QtWidgets
from PySide6.QtWidgets import QWidget, QStackedWidget
import open3d as o3d

from src.gui.windows.visualization.rasterization_window import RasterizationWindow
from src.gui.windows.visualization.open3d_window import Open3DWindow


class VisualizerWindow(QWidget):
    def __init__(self, parent):
        super(VisualizerWindow, self).__init__()
        self.parent_window = parent
        self.layout = QtWidgets.QGridLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.setBaseSize(self.maximumSize())

        self.vis_stack = QStackedWidget()
        self.vis_open3d = Open3DWindow(self)
        self.vis_raster = RasterizationWindow()
        self.vis_stack.addWidget(self.vis_open3d)
        self.vis_stack.addWidget(self.vis_raster)
        self.vis_stack.setCurrentIndex(0)

        self.layout.addWidget(self.vis_stack)
        self.vis_open3d.set_active(True)

        self.o3d_pc1 = self.vis_open3d.pc1
        self.o3d_pc2 = self.vis_open3d.pc2
        self.gauss_pc1 = None
        self.gauss_pc2 = None

    def load_point_clouds(self, o3d_pc1, o3d_pc2, gauss_pc1=None, gauss_pc2=None, keep_view=False,
                          transformation_matrix=None, debug_color1=None, debug_color2=None):
        self.o3d_pc1 = o3d_pc1
        self.o3d_pc2 = o3d_pc2
        self.gauss_pc1 = gauss_pc1
        self.gauss_pc2 = gauss_pc2

        self.vis_open3d.load_point_clouds(o3d_pc1, o3d_pc2, keep_view, transformation_matrix, debug_color1,
                                          debug_color2)

        if gauss_pc1 is None:
            return

        self.vis_raster.load_point_clouds(gauss_pc1, gauss_pc2, transformation_matrix)

    def on_embed_button_pressed(self):
        if self.vis_stack.currentIndex() == 0:
            self.vis_open3d.on_embed_button_pressed()
            return

        self.vis_raster.on_embed_button_pressed()

    def vis_type_changed(self, index):
        if index == 0:
            self.vis_open3d.set_active(True)
            self.vis_raster.set_active(False)
        else:
            self.vis_open3d.set_active(False)
            self.vis_raster.set_active(True)

        self.vis_stack.setCurrentIndex(index)

    def update_transform(self, transformation, dc1, dc2):
        self.vis_open3d.update_transform(transformation, dc1, dc2)
        self.vis_raster.update_transform(transformation)

    def update_visualizer_settings_o3d(self, zoom, front, lookat, up):
        self.vis_open3d.update_visualizer(zoom, front, lookat, up)

    def get_current_view(self):
        if self.vis_stack.currentIndex() == 0:
            return self.vis_open3d.get_current_view()

        self.vis_raster.get_current_view()

    def is_ortho(self):
        if self.vis_stack.currentIndex() == 0:
            return self.vis_open3d.is_ortho()

        return False

    def get_current_camera(self):
        if self.vis_stack.currentIndex() == 0:
            self.vis_open3d.get_camera_model()
            return

        self.vis_raster.get_camera_model()

    def apply_camera_transformation(self, transformation):
        if self.vis_stack.currentIndex() == 0:
            self.vis_open3d.apply_camera_transformation(transformation)
            return

        self.vis_raster.apply_camera_transformation(transformation)
