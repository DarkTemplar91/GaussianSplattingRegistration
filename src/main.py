import argparse
import sys

import qdarkstyle
from PyQt5.QtWidgets import QApplication

from src.gui.windows.main_window import RegistrationMainWindow


def parse_args():
    parser = argparse.ArgumentParser(
        description="Registers and merges two gaussian splatting point clouds.")
    # TODO: Add back command line support
    parser.add_argument("--path_input_first", default=r"")
    parser.add_argument("--path_input_second", default=r"")
    parser.add_argument("--path_trained_first",
                        default=r"")
    parser.add_argument("--path_trained_second",
                        default=r"")
    parser.add_argument("--output_path",
                        default=r"")
    parser.add_argument("--skip_global", type=bool, default=True)
    parser.add_argument("--global_type", default="default", choices=["default", "fast"])

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    PC_INPUT_PATH_FIRST = args.path_input_first
    PC_INPUT_PATH_SECOND = args.path_input_second
    PC_TRAINED_PATH_FIRST = args.path_trained_first
    PC_TRAINED_PATH_SECOND = args.path_trained_second
    OUTPUT_PATH = args.output_path
    SKIP_GLOBAL_REGISTRATION = args.skip_global
    GLOBAL_REGISTRATION_TYPE = args.global_type

    app = QApplication([])
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
    form = RegistrationMainWindow()
    form.show()
    sys.exit(app.exec())
