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
    form = RegistrationMainWindow()
    form.show()
    sys.exit(app.exec())
