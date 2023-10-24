from PyQt5.QtWidgets import QLabel, QVBoxLayout, QGroupBox, QComboBox


# TODO: Finish
class GlobalRegistrationGroup(QGroupBox):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setTitle("Global registration")

        type_label = QLabel("Global registration type")
        combo_box_global = QComboBox()
        # TODO: Use enums
        combo_box_global.addItems(["Default", "Fast"])

        layout.addWidget(type_label)
        layout.addWidget(combo_box_global)
        layout.addStretch()
