from PyQt5 import QtCore
from PyQt5.QtCore import QLocale
from PyQt5.QtGui import QDoubleValidator, QIntValidator
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit, QSizePolicy, \
    QComboBox

from src.gui.widgets.registration_input_field_widget import RegistrationInputField
from src.utils.local_registration_util import LocalRegistrationType


class LocalRegistrationTab(QWidget):
    signal_do_registration = QtCore.pyqtSignal(LocalRegistrationType, float, float, float, int)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        type_label = QLabel("Local registration type")
        self.combo_box_icp = QComboBox()
        self.combo_box_icp.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        locale = QLocale(QLocale.English)
        double_validator = QDoubleValidator()
        double_validator.setLocale(locale)
        double_validator.setRange(0.0, 9999.0)
        double_validator.setDecimals(10)

        int_validator = QIntValidator()
        int_validator.setLocale(locale)
        int_validator.setRange(0, 9999)

        for enum_member in LocalRegistrationType:
            self.combo_box_icp.addItem(enum_member.instance_name)

        # Max correspondence
        self.correspondence_widget = RegistrationInputField("Max correspondence:", "5.0", 150, 60,
                                                            double_validator)

        convergence_layout = QVBoxLayout()
        convergence_widget = QWidget()
        convergence_widget.setLayout(convergence_layout)

        # Convergence criteria
        conv_label = QLabel("Convergence criteria")
        conv_label.setStyleSheet(
            "QLabel {"
            "    font-size: 12px;"
            "    font-weight: bold;"
            "    padding: 8px;"
            "}"
        )

        # Relative fitness
        self.fitness_widget = RegistrationInputField("Relative fitness:", "0.000001", 100, 60,
                                                     double_validator)

        # Relative RMSE
        self.rmse_widget = RegistrationInputField("Relative RMSE:", "0.000001", 100, 60,
                                                  double_validator)

        # Max iterations
        self.iteration_widget = RegistrationInputField("Max iteration:", "30", 100, 60,
                                                       int_validator)

        convergence_layout.addWidget(self.fitness_widget)
        convergence_layout.addWidget(self.rmse_widget)
        convergence_layout.addWidget(self.iteration_widget)

        bt_apply = QPushButton("Start local registration")
        bt_apply.setStyleSheet("padding-left: 10px; padding-right: 10px;"
                               "padding-top: 2px; padding-bottom: 2px;")
        bt_apply.setFixedSize(250, 30)
        bt_apply.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        layout.addWidget(type_label)
        layout.addWidget(self.combo_box_icp)
        layout.addWidget(self.correspondence_widget)
        layout.addSpacing(5)
        layout.addWidget(conv_label)
        layout.addWidget(convergence_widget)
        layout.addWidget(bt_apply)
        layout.addStretch()

        bt_apply.clicked.connect(self.registration_button_pressed)

    def registration_button_pressed(self):
        registration_type = LocalRegistrationType(self.combo_box_icp.currentIndex())
        max_correspondence = float(self.correspondence_widget.lineedit.text())
        relative_fitness = float(self.fitness_widget.lineedit.text())
        relative_rmse = float(self.rmse_widget.lineedit.text())
        max_iteration = int(self.iteration_widget.lineedit.text())
        self.signal_do_registration.emit(registration_type,
                                         max_correspondence, relative_fitness, relative_rmse, max_iteration)
