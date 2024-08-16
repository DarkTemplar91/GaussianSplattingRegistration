import copy
import sys
from subprocess import Popen, PIPE

import numpy as np
import open3d as o3d
from PySide6.QtCore import Qt

if sys.platform.startswith('win'):
    import win32gui

from PySide6 import QtGui, QtWidgets, QtCore
from PySide6.QtWidgets import QMainWindow


class Open3DWindow(QMainWindow):
    def __init__(self):
        super(Open3DWindow, self).__init__()
        self.pc1_copy = None
        self.pc2_copy = None
        self.pc1 = None
        self.pc2 = None

        self.parent_widget = QtWidgets.QWidget()
        self.layout = QtWidgets.QGridLayout(self.parent_widget)
        self.setCentralWidget(self.parent_widget)

        self.vis = o3d.visualization.Visualizer()
        self.vis.create_window()
        self.is_embedded = True

        # Set background color to match theme
        background_color = (0.09803921568627451, 0.13725490196078433, 0.17647058823529413)
        opt = self.vis.get_render_option()
        opt.background_color = background_color

        self.hwnd = None
        platform = sys.platform
        if platform.startswith("win"):
            self.hwnd = win32gui.FindWindowEx(0, 0, None, "Open3D")
        elif platform.startswith("linux"):
            self.hwnd = self.get_hwnd()

        self.window = QtGui.QWindow.fromWinId(self.hwnd)
        self.window_container = self.createWindowContainer(self.window, self.parent_widget)
        self.layout.addWidget(self.window_container, 0, 0)
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_vis)
        timer.start(1)

        # Example data
        demo_icp_pcds = o3d.data.DemoICPPointClouds()
        source = o3d.io.read_point_cloud(demo_icp_pcds.paths[0])
        target = o3d.io.read_point_cloud(demo_icp_pcds.paths[1])

        self.pc1_copy = source
        self.pc2_copy = target
        self.pc1 = source
        self.pc2 = target
        self.vis.add_geometry(self.pc1_copy)
        self.vis.add_geometry(self.pc2_copy)

    def update_vis(self):
        self.vis.poll_events()
        self.vis.update_renderer()

    def load_point_clouds(self, point_cloud_first, point_cloud_second, keep_view=False,
                          transformation_matrix=None, debug_color1=None, debug_color2=None):
        self.pc1 = point_cloud_first
        self.pc2 = point_cloud_second
        self.pc1_copy = copy.deepcopy(self.pc1)
        self.pc2_copy = copy.deepcopy(self.pc2)

        camera_params = None
        if keep_view:
            ctr = self.vis.get_view_control()
            camera_params = ctr.convert_to_pinhole_camera_parameters()

        if debug_color1 is not None and debug_color2 is not None:
            self.pc1_copy.paint_uniform_color(debug_color1)
            self.pc2_copy.paint_uniform_color(debug_color2)

        if transformation_matrix is not None:
            self.pc1_copy.transform(transformation_matrix)

        self.vis.clear_geometries()
        self.vis.add_geometry(self.pc1_copy)
        self.vis.add_geometry(self.pc2_copy)

        if keep_view and camera_params is not None:
            self.vis.get_view_control().convert_from_pinhole_camera_parameters(camera_params)

    def closeEvent(self, event):
        self.vis.destroy_window()
        super(QMainWindow, self).closeEvent(event)

    def update_transform(self, transformation, debug_color1=None, debug_color2=None):
        if not self.pc1 or not self.pc2:
            return

        ctr = self.vis.get_view_control()
        camera_params = ctr.convert_to_pinhole_camera_parameters()

        self.pc1_copy = copy.deepcopy(self.pc1)
        self.pc2_copy = copy.deepcopy(self.pc2)

        if debug_color1 is not None and debug_color2 is not None:
            self.pc1_copy.paint_uniform_color(debug_color1)
            self.pc2_copy.paint_uniform_color(debug_color2)

        self.pc1_copy.transform(transformation)

        self.vis.clear_geometries()
        self.vis.add_geometry(self.pc1_copy)
        self.vis.add_geometry(self.pc2_copy)

        self.vis.get_view_control().convert_from_pinhole_camera_parameters(camera_params)

    def update_visualizer(self, zoom, front, lookat, up):
        view_control = self.vis.get_view_control()
        view_control.set_zoom(zoom)
        view_control.set_front(front)
        view_control.set_lookat(lookat)
        view_control.set_up(up)

    def get_current_view(self):
        view_control = self.vis.get_view_control()
        parameters = view_control.convert_to_pinhole_camera_parameters()
        extrinsic = parameters.extrinsic

        up = -extrinsic[1:2, 0:3].transpose()
        front = -extrinsic[2:3, 0:3].transpose()
        eye = np.linalg.inv(extrinsic[0:3, 0:3]) @ (extrinsic[0:3, 3:4] * -1.0)

        aabb = self.calculate_aabb()

        tan_half_fov = parameters.intrinsic.height / (parameters.intrinsic.intrinsic_matrix[1, 1] * 2.0)
        fov_rad = np.arctan(tan_half_fov) * 2.0
        fov = fov_rad * 180.0 / np.pi
        fov = np.max([np.min([fov, 90.0]), 50.0])

        bb_center = aabb.get_center()
        subtracted = (eye.reshape(3) - bb_center)
        ideal_distance = np.abs(subtracted.dot(front))[0]
        ideal_zoom = ideal_distance * np.tan(fov * 0.5 / 180.0 * np.pi) / aabb.get_max_extent()

        zoom = max([min([ideal_zoom, 2.0]), 0.02])
        view_ratio = zoom * aabb.get_max_extent()
        distance = view_ratio / np.tan(fov * 0.5 / 180.0 * np.pi)
        lookat = eye - front * distance

        return zoom, front.flatten(), lookat.flatten(), up.flatten()

    def calculate_aabb(self):
        combined_vertices = o3d.utility.Vector3dVector()
        combined_vertices.extend(self.pc1_copy.points)
        combined_vertices.extend(self.pc2_copy.points)
        aabb = o3d.geometry.AxisAlignedBoundingBox()
        aabb = aabb.create_from_points(combined_vertices)
        return aabb

    @staticmethod
    def get_hwnd():
        hwnd = None
        while hwnd is None:
            proc = Popen('wmctrl -l', stdin=None, stdout=PIPE, stderr=None, shell=True)
            out, err = proc.communicate()
            for window in out.decode('utf-8').split('\n'):
                if 'Open3D' in window:
                    hwnd = int(window.split(' ')[0], 16)
                    return hwnd

    def get_camera_extrinsic(self):
        view_control = self.vis.get_view_control()
        parameters = view_control.convert_to_pinhole_camera_parameters()
        return parameters.extrinsic

    def get_camera_intrinsic(self):
        view_control = self.vis.get_view_control()
        parameters = view_control.convert_to_pinhole_camera_parameters()
        return parameters.intrinsic.intrinsic_matrix

    # FOV of 5 means that Open3D uses ortho projection
    def is_ortho(self):
        return self.vis.get_view_control().get_field_of_view() == 5

    def apply_camera_transformation(self, extrinsics):
        view_control = self.vis.get_view_control()
        parameters = view_control.convert_to_pinhole_camera_parameters()
        parameters.extrinsic = extrinsics
        view_control.convert_from_pinhole_camera_parameters(parameters)
        pass

    def pop_visualizer(self):
        if self.is_embedded:
            self.layout.removeWidget(self.window_container)
            self.window.setParent(None)
            self.window.setFlags(Qt.WindowType.Window)
            self.is_embedded = False
            return

        self.window = QtGui.QWindow.fromWinId(self.hwnd)
        self.window_container = self.createWindowContainer(self.window, self.parent_widget)
        self.layout.addWidget(self.window_container, 0, 0)
        self.is_embedded = True
