import copy
import sys
from subprocess import Popen, PIPE

import numpy as np
import open3d as o3d
from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import QMainWindow, QWidget

from src.models.camera import Camera
from src.utils.graphics_utils import get_focal_from_intrinsics, get_dimension_from_intrinsics

platform = sys.platform
if platform.startswith('win'):
    import win32gui
    import win32con

if platform.startswith('linux'):
    from Xlib import display, X


class Open3DWindow(QWidget):
    def __init__(self, parent):
        super(Open3DWindow, self).__init__()
        self.pc1_copy = None
        self.pc2_copy = None
        self.pc1 = None
        self.pc2 = None
        self.parent_window = parent
        self.layout = QtWidgets.QGridLayout(self)

        self.vis = o3d.visualization.Visualizer()
        self.vis.create_window()
        self.is_embedded = False

        self.setBaseSize(self.maximumSize())

        # Set background color to match theme
        background_color = (0.09803921568627451, 0.13725490196078433, 0.17647058823529413)
        opt = self.vis.get_render_option()
        opt.background_color = background_color

        self.hwnd = self.get_hwnd()

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_vis)

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
        self.vis.close()
        super().closeEvent(event)

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
        if platform.startswith('win'):
            hwnd = win32gui.FindWindowEx(0, 0, None, "Open3D")
        elif platform.startswith('linux'):
            hwnd = Open3DWindow.get_hwnd_linux()

        return hwnd

    @staticmethod
    def get_hwnd_linux():
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

    def showEvent(self, event):
        super().showEvent(event)
        self.is_embedded = self.embed_window()

    def embed_window(self):
        if platform.startswith('win'):
            return self.__embed_window_win()

        if platform.startswith('linux'):
            return self.__embed_window_linux()

    def pop_window(self):
        if platform.startswith('win'):
            return self.__pop_window_win()

        if platform.startswith('linux'):
            return self.__pop_window_linux()

    def on_embed_button_pressed(self):
        if self.is_embedded:
            self.is_embedded = self.pop_window()
            return

        self.is_embedded = self.embed_window()

    def __embed_window_win(self):
        if not self.hwnd:
            return False

        win32gui.SetWindowLong(
            self.hwnd,
            win32con.GWL_STYLE,
            win32con.WS_VISIBLE | win32con.WS_CHILD
        )

        win32gui.SetParent(self.hwnd, self.winId())

        # Resize and move the window to fit within the PySide6 window
        rect = self.rect()
        win32gui.MoveWindow(self.hwnd, rect.left(), rect.top(), rect.width(), rect.height(), True)

        return True

    def __embed_window_linux(self):
        if not self.hwnd:
            return False

        dsp = display.Display()
        app_window = dsp.create_resource_object('window', self.hwnd)
        pyqt_window_id = self.winId()

        app_window.reparent(pyqt_window_id, 0, 0)
        app_window.map()
        rect = self.rect()
        app_window.configure(width=rect.width(), height=rect.height())

        dsp.sync()

        return True

    def __pop_window_win(self):
        if not self.hwnd:
            return True

        win32gui.SetWindowLong(
            self.hwnd,
            win32con.GWL_STYLE,
            win32con.WS_VISIBLE | win32con.WS_OVERLAPPEDWINDOW
        )

        win32gui.SetParent(self.hwnd, win32gui.GetDesktopWindow())
        win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)

        return False

    def __pop_window_linux(self):
        if not self.hwnd:
            return True

        dsp = display.Display()
        app_window = dsp.create_resource_object('window', self.hwnd)

        root = dsp.screen().root
        app_window.reparent(root, 0, 0)

        app_window.configure(stack_mode=X.Above)
        dsp.sync()

        return False

    def set_active(self, active):
        self.timer.start(1) if active else self.timer.stop()

    def get_camera_model(self):
        camera_mat = self.get_camera_extrinsic().astype(np.float32).transpose()
        R = camera_mat[:3, :3]
        T = camera_mat[3, :3]
        intrinsics = self.get_camera_intrinsic()
        fx, fy = get_focal_from_intrinsics(intrinsics)
        width, height = get_dimension_from_intrinsics(intrinsics)
        return Camera(R, T, fx, fy, "", width, height)
