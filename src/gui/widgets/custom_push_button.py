from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSizePolicy


class CustomPushButton(QWidget):

    def __init__(self, value: str, stretch_percent: int):
        super().__init__()

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.stretch_percent = stretch_percent

        self.button = QPushButton(value)
        self.button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.button.setFixedHeight(30)
        self.button.setStyleSheet("padding-top: 0.5em; padding-bottom: 0.5em;")
        layout.addStretch()
        layout.addWidget(self.button)
        layout.addStretch()

        # Set stretch factors to control the proportion of space
        # Calculate stretch factors based on percentage
        total_stretch = 100 - self.stretch_percent
        left_right_stretch = total_stretch / 2

        layout.setStretch(0, int(left_right_stretch))
        layout.setStretch(2, int(left_right_stretch))
        layout.setStretch(1, int(stretch_percent))

    def connect_to_clicked(self, function):
        self.button.clicked.connect(function)
