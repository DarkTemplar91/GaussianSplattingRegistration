from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit


class SimpleInputField(QWidget):

    def __init__(self, label_text, value, label_width=150, line_edit_width=60, validator=None):
        super().__init__()

        layout = QHBoxLayout()
        self.setLayout(layout)

        label = QLabel(label_text)
        label.setFixedWidth(label_width)
        self.lineedit = QLineEdit(value)
        self.lineedit.setFixedWidth(line_edit_width)
        self.lineedit.setValidator(validator)

        layout.addWidget(label)
        layout.addWidget(self.lineedit)
        layout.addStretch()
