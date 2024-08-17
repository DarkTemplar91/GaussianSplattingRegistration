from PySide6.QtCore import Qt
from PySide6.QtWidgets import QProgressDialog


class ProgressDialogFactory:

    @staticmethod
    def get_progress_dialog(title: str, label: str, close_function=None):
        progress_dialog = QProgressDialog()
        progress_dialog.setMinimumDuration(0)
        progress_dialog.setMinimum(0)
        progress_dialog.setMaximum(100)
        progress_dialog.setValue(0)
        progress_dialog.setWindowTitle(title)
        progress_dialog.setLabelText(label)
        progress_dialog.setModal(True)
        if close_function is not None:
            progress_dialog.canceled.connect(close_function)

        return progress_dialog
