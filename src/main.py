import json
import os
import sys

import numpy as np
import qdarkstyle
import torch
from PySide6.QtCore import QLocale
from PySide6.QtWidgets import QApplication

from src.gui.windows.interactive_viewer_window import InteractiveImageViewer
from src.models.cameras import Camera
from src.utils.file_loader import load_gaussian_pc
from src.utils.general_utils import convert_to_camera_transform

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))
from src.gui.windows.main_window import RegistrationMainWindow

if __name__ == '__main__':
    sys.path.append('src/cpp_ext')
    locale = QLocale(QLocale.Language.C)
    locale.setNumberOptions(QLocale.NumberOption.RejectGroupSeparator)
    QLocale.setDefault(locale)
    app = QApplication()
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyside6'))
    """form = RegistrationMainWindow()
    form.show()"""

    # D:\Egyetem\Szakdoga\TestData\Blender\lego_full\point_cloud\iteration_30000
    _, point_cloud = load_gaussian_pc("D:/Egyetem/Szakdoga/TestData/Blender/lego_full/point_cloud/iteration_30000/point_cloud.ply")
    point_cloud.move_to_device("cuda:0")
    mean = torch.mean(point_cloud.get_xyz, dim=0)
    f = open("D:/Egyetem/Szakdoga/TestData/Blender/lego_full/cameras.json")
    cameras_list = []
    data = json.load(f)
    for camera_iter in data:
        fx = camera_iter["fx"]
        fy = camera_iter["fy"]
        height = camera_iter["height"]
        width = camera_iter["width"]

        rot = np.array([np.array(xi) for xi in camera_iter["rotation"]])
        pos = np.array([np.array(xi) for xi in camera_iter["position"]])
        R, T = convert_to_camera_transform(rot, pos)
        image_name = camera_iter["img_name"]
        camera = Camera(R, T, fx, fy, image_name, 1600, 900, target=mean)
        cameras_list.append(camera)
    viewer = InteractiveImageViewer(point_cloud, cameras_list[0])
    viewer.show()
    sys.exit(app.exec())
