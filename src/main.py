import sys
import qdarkstyle
from PyQt5.QtWidgets import QApplication

from src.gui.windows.main_window import RegistrationMainWindow

if __name__ == '__main__':
    sys.path.append('src/cpp_ext')
    app = QApplication([])
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
    form = RegistrationMainWindow()
    form.show()
    sys.exit(app.exec())
