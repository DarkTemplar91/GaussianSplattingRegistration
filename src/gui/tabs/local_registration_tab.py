from PyQt5 import QtCore
from PyQt5.QtCore import QLocale, Qt
from PyQt5.QtGui import QDoubleValidator, QIntValidator, QPalette
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QSizePolicy, \
    QComboBox, QScrollArea, QFrame, QHBoxLayout

from src.gui.widgets.optional_value_widget import OptionalInputField
from src.gui.widgets.registration_input_field_widget import SimpleInputField
from src.utils.local_registration_util import LocalRegistrationType, KernelLossFunctionType


class LocalRegistrationTab(QWidget):
    signal_do_registration = QtCore.pyqtSignal(LocalRegistrationType, float, float, float, int,
                                               KernelLossFunctionType, float)

    def __init__(self):
        super().__init__()

        registration_layout = QVBoxLayout()
        self.setLayout(registration_layout)

        scroll_widget = QScrollArea()
        scroll_widget.setBackgroundRole(QPalette.Background)
        scroll_widget.setFrameShadow(QFrame.Plain)
        scroll_widget.setFrameShape(QFrame.NoFrame)
        scroll_widget.setWidgetResizable(True)

        inner_widget = QWidget()
        layout = QVBoxLayout()
        inner_widget.setLayout(layout)
        scroll_widget.setWidget(inner_widget)

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
        self.correspondence_widget = SimpleInputField("Max correspondence:", "5.0", 150, 60,
                                                      double_validator)

        # Convergence criteria
        convergence_layout = QVBoxLayout()
        convergence_widget = QWidget()
        convergence_widget.setLayout(convergence_layout)

        conv_label = QLabel("Convergence criteria")
        conv_label.setStyleSheet(
            "QLabel {"
            "    font-size: 12px;"
            "    font-weight: bold;"
            "    padding: 8px;"
            "}"
        )

        # Relative fitness
        self.fitness_widget = SimpleInputField("Relative fitness:", "0.000001", 100, 60,
                                               double_validator)

        # Relative RMSE
        self.rmse_widget = SimpleInputField("Relative RMSE:", "0.000001", 100, 60,
                                            double_validator)

        # Max iterations
        self.iteration_widget = SimpleInputField("Max iteration:", "30", 100, 60,
                                                 int_validator)

        convergence_layout.addWidget(self.fitness_widget)
        convergence_layout.addWidget(self.rmse_widget)
        convergence_layout.addWidget(self.iteration_widget)

        # Outlier rejection
        outlier_layout = QVBoxLayout()
        outlier_widget = QWidget()
        outlier_widget.setLayout(outlier_layout)

        rejection_label = QLabel("Robust Kernel outlier rejection")
        rejection_label.setStyleSheet(
            "QLabel {"
            "    font-size: 12px;"
            "    font-weight: bold;"
            "    padding: 8px;"
            "}"
        )

        self.k_value_widget = SimpleInputField("Standard deviation", "0.0",
                                               100, validator=double_validator)
        self.k_value_widget.setEnabled(False)
        outlier_type_label = QLabel("Loss type:")
        self.combo_box_outlier = QComboBox()
        self.combo_box_outlier.currentIndexChanged.connect(self.rejection_type_changed)
        self.combo_box_outlier.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        for enum_member in KernelLossFunctionType:
            self.combo_box_outlier.addItem(enum_member.instance_name)

        rejection_widget = QWidget()
        rejection_layout = QHBoxLayout()
        rejection_widget.setLayout(rejection_layout)
        rejection_layout.addWidget(outlier_type_label)
        rejection_layout.addWidget(self.combo_box_outlier)
        rejection_layout.addStretch()

        outlier_layout.addWidget(rejection_widget)
        outlier_layout.addWidget(self.k_value_widget)

        bt_apply = QPushButton("Start local registration")
        bt_apply.setStyleSheet("padding-left: 10px; padding-right: 10px;"
                               "padding-top: 2px; padding-bottom: 2px;")
        bt_apply.setFixedHeight(30)
        bt_apply.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout.addWidget(type_label)
        layout.addWidget(self.combo_box_icp)
        layout.addWidget(self.correspondence_widget)
        layout.addSpacing(5)
        layout.addWidget(conv_label)
        layout.addWidget(convergence_widget)
        layout.addWidget(rejection_label)
        layout.addWidget(outlier_widget)
        layout.addStretch()

        registration_layout.addWidget(scroll_widget)
        registration_layout.addWidget(bt_apply)

        bt_apply.clicked.connect(self.registration_button_pressed)

    def registration_button_pressed(self):
        registration_type = LocalRegistrationType(self.combo_box_icp.currentIndex())
        max_correspondence = float(self.correspondence_widget.lineedit.text())
        relative_fitness = float(self.fitness_widget.lineedit.text())
        relative_rmse = float(self.rmse_widget.lineedit.text())
        max_iteration = int(self.iteration_widget.lineedit.text())
        rejection_type = KernelLossFunctionType(self.combo_box_outlier.currentIndex())
        k_value = float(self.k_value_widget.lineedit.text())
        self.signal_do_registration.emit(registration_type,
                                         max_correspondence, relative_fitness, relative_rmse, max_iteration,
                                         rejection_type, k_value)

    def rejection_type_changed(self, index):
        self.k_value_widget.setEnabled(index != 0)
