from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit


class SimpleInputField(QWidget):

    def __init__(self, value, line_edit_width=60, validator=None):
        super().__init__()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.lineedit = QLineEdit(value)
        self.lineedit.setFixedWidth(line_edit_width)
        self.lineedit.setValidator(validator)

        layout.addWidget(self.lineedit)
        layout.addStretch()

    def text(self):
        return self.lineedit.text()

    def setText(self, value):
        self.lineedit.setText(value)
