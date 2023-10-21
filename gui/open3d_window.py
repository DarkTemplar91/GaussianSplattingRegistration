import open3d as o3d
import win32gui
from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QOpenGLWidget, QMainWindow


class Open3DWindow(QMainWindow):
    def __init__(self):
        super(Open3DWindow, self).__init__()
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QGridLayout(widget)
        self.setCentralWidget(widget)

        self.vis = o3d.visualization.Visualizer()
        self.vis.create_window()

        # Set background color to match theme
        background_color = (0.09803921568627451, 0.13725490196078433, 0.17647058823529413)  # RGB values for white
        opt = self.vis.get_render_option()
        opt.background_color = background_color

        # TODO: Find workaround for linux/mac
        hwnd = win32gui.FindWindowEx(0, 0, None, "Open3D")
        self.window = QtGui.QWindow.fromWinId(hwnd)
        self.window_container = self.createWindowContainer(self.window, widget)
        layout.addWidget(self.window_container, 0, 0)
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_vis)
        timer.start(1)

        # Example data
        knot_mesh = o3d.data.KnotMesh()
        mesh = o3d.io.read_triangle_mesh(knot_mesh.path)
        mesh.compute_vertex_normals()
        self.vis.add_geometry(mesh)

    def update_vis(self):
        # self.vis.update_geometry()
        self.vis.poll_events()
        self.vis.update_renderer()

    def load_point_clouds(self, point_cloud_first, point_cloud_second):
        self.vis.clear_geometries()
        self.vis.add_geometry(point_cloud_first)
        self.vis.add_geometry(point_cloud_second)
