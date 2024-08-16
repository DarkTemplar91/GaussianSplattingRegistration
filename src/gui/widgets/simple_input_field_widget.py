from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit
import src.utils.graphics_utils as graphic_util


class SimpleInputField(QWidget):

    def __init__(self, label_text, value, label_width=150, line_edit_width=60, validator=None):
        super().__init__()

        layout = QHBoxLayout()
        self.setLayout(layout)

        self.label = QLabel(label_text)
        self.label.setFixedWidth(int(label_width * graphic_util.SIZE_SCALE_X))
        self.lineedit = QLineEdit(value)
        self.lineedit.setFixedWidth(int(line_edit_width * graphic_util.SIZE_SCALE_X))
        self.lineedit.setValidator(validator)

        layout.addWidget(self.label)
        layout.addWidget(self.lineedit)
        layout.addStretch()
