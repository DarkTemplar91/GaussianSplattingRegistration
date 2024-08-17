import sys
import qdarkstyle
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from src.gui.windows.main_window import RegistrationMainWindow

if __name__ == '__main__':
    sys.path.append('src/cpp_ext')
    app = QApplication([])
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyside6'))
    form = RegistrationMainWindow()
    form.show()
    sys.exit(app.exec())
