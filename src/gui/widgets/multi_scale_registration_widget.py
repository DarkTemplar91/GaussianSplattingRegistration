from PyQt5 import QtCore
from PyQt5.QtCore import QLocale, QRegularExpression
from PyQt5.QtGui import QDoubleValidator, QRegularExpressionValidator
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QComboBox, QCheckBox, QSizePolicy, QPushButton

from src.gui.widgets.file_selector_widget import FileSelector
from src.gui.widgets.registration_input_field_widget import RegistrationInputField
from src.utils.local_registration_util import LocalRegistrationType


class MultiScaleRegistrationTab(QWidget):
    signal_do_registration = QtCore.pyqtSignal(bool, str, str, LocalRegistrationType, float, float, list, list)

    def __init__(self, input_path):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        # validators
        locale = QLocale(QLocale.English)
        double_validator = QDoubleValidator()
        double_validator.setLocale(locale)
        double_validator.setRange(0.0, 9999.0)
        double_validator.setDecimals(10)

        double_list_validator = QRegularExpressionValidator()
        double_list_validator.setLocale(locale)
        regex_double = QRegularExpression("(?!0\\d)(\\d+(\\.\\d+)?)(,(-?(?!0\\d)(\\d+(\\.\\d+)?)))*")
        double_list_validator.setRegularExpression(regex_double)

        int_list_validator = QRegularExpressionValidator()
        int_list_validator.setLocale(locale)
        regex_int = QRegularExpression("(?!0\\d)\\d+(,(-?(?!0\\d)\\d+))*")
        int_list_validator.setRegularExpression(regex_int)

        label_title = QLabel("Multi-scale Local Registration")
        label_title.setStyleSheet(
            "QLabel {"
            "    font-size: 14px;"
            "    font-weight: bold;"
            "    padding: 8px;"
            "}"
        )

        self.sparse_checkbox = QCheckBox()
        self.sparse_checkbox.setText("Use corresponding sparse inputs for initial registration")
        self.sparse_checkbox.setStyleSheet(
            "QCheckBox::indicator {"
            "    width: 20px;"
            "    height: 20px;"
            "}"
            "QCheckBox::indicator::text {"
            "    padding-left: 10px;"
            "}"
        )
        self.sparse_checkbox.stateChanged.connect(self.checkbox_changed)

        # File selectors for sparse input
        self.fs_sparse1 = FileSelector(text="First sparse input:", base_path=input_path)
        self.fs_sparse2 = FileSelector(text="Second sparse input:", base_path=input_path)
        self.fs_sparse1.setEnabled(False)
        self.fs_sparse2.setEnabled(False)

        # Local registration type
        type_label = QLabel("Local registration type")
        self.combo_box_icp = QComboBox()
        self.combo_box_icp.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        for enum_member in LocalRegistrationType:
            self.combo_box_icp.addItem(enum_member.instance_name)

        # Relative fitness
        self.fitness_widget = RegistrationInputField("Relative fitness:", "0.000001", 90, 60,
                                                     double_validator)

        # Relative RMSE
        self.rmse_widget = RegistrationInputField("Relative RMSE:", "0.000001", 90, 60,
                                                  double_validator)

        self.voxel_values = RegistrationInputField("Voxel values:", "5,2.5", 90, 150, double_list_validator)
        self.iter_values = RegistrationInputField("Iteration values:", "50,30", 90, 150, int_list_validator)

        bt_apply = QPushButton("Start multi-scale registration")
        bt_apply.setStyleSheet("padding-left: 10px; padding-right: 10px;"
                               "padding-top: 2px; padding-bottom: 2px;")
        bt_apply.setFixedSize(250, 30)
        bt_apply.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        bt_apply.clicked.connect(self.registration_button_pressed)

        layout.addWidget(label_title)
        layout.addWidget(self.sparse_checkbox)
        layout.addWidget(self.fs_sparse1)
        layout.addWidget(self.fs_sparse2)
        layout.addWidget(type_label)
        layout.addWidget(self.combo_box_icp)

        layout.addWidget(self.fitness_widget)
        layout.addWidget(self.rmse_widget)

        layout.addWidget(self.voxel_values)
        layout.addWidget(self.iter_values)
        layout.addWidget(bt_apply)
        layout.addStretch()

    def checkbox_changed(self, state):
        self.fs_sparse1.setEnabled(state)
        self.fs_sparse2.setEnabled(state)

        if state:
            return

        self.fs_input1.inputField.setText("")
        self.fs_input1.file_path = ""

        self.fs_input2.inputField.setText("")
        self.fs_input2.file_path = ""

    def registration_button_pressed(self):
        use_corresponding = self.sparse_checkbox.isChecked()
        sparse_first = self.fs_sparse1.file_path
        sparse_second = self.fs_sparse2.file_path
        registration_type = LocalRegistrationType(self.combo_box_icp.currentIndex())
        relative_fitness = float(self.fitness_widget.lineedit.text())
        relative_rmse = float(self.rmse_widget.lineedit.text())

        voxel_values = list(filter(None, self.voxel_values.lineedit.text().split(",")))
        iter_values = list(filter(None, self.iter_values.lineedit.text().split(",")))
        self.signal_do_registration.emit(use_corresponding, sparse_first, sparse_second, registration_type,
                                         relative_fitness, relative_rmse, voxel_values, iter_values)

