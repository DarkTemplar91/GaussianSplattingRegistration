from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QCheckBox
import src.utils.graphics_utils as graphic_util


class OptionalInputField(QWidget):

    def __init__(self, label_text, value, label_width=150, line_edit_width=60, validator=None):
        super().__init__()

        layout = QHBoxLayout()
        self.setLayout(layout)

        self.checkbox_optional = QCheckBox()
        self.checkbox_optional.setStyleSheet(
            "QCheckBox::indicator {"
            f"    width: 20px;"
            f"    height: 20px;"
            "}"
            "QCheckBox::indicator::text {"
            f"    padding-left: 10px;"
            "}"
        )

        label = QLabel(label_text)
        label.setFixedWidth(label_width)
        self.voxel_size_lineedit = QLineEdit(value)
        self.voxel_size_lineedit.setFixedWidth(line_edit_width)
        self.voxel_size_lineedit.setValidator(validator)
        self.voxel_size_lineedit.setEnabled(False)

        layout.addWidget(self.checkbox_optional)
        layout.addWidget(label)
        layout.addWidget(self.voxel_size_lineedit)
        layout.addStretch()

        self.checkbox_optional.stateChanged.connect(self.checkbox_changed)

    def checkbox_changed(self, state):
        self.voxel_size_lineedit.setEnabled(state)

    def get_value(self):
        return self.voxel_size_lineedit.text() if self.checkbox_optional.isChecked() else ""

    def is_checked(self):
        return self.checkbox_optional.isChecked()
