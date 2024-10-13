import os
import sys

import qdarkstyle
from PySide6.QtCore import QLocale
from PySide6.QtWidgets import QApplication

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
