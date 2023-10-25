from PyQt5 import QtCore
from PyQt5.QtCore import QLocale
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit, QSizePolicy, \
    QGroupBox, QComboBox

from src.utils.local_registration_util import LocalRegistrationType


class LocalRegistrationGroup(QGroupBox):

    signal_do_registration = QtCore.pyqtSignal(LocalRegistrationType, float, float, float, float)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setTitle("Local registration")

        type_label = QLabel("Local registration type")
        self.combo_box_icp = QComboBox()

        locale = QLocale(QLocale.English)
        double_validator = QDoubleValidator()
        double_validator.setLocale(locale)
        double_validator.setRange(0.0, 9999.0)
        double_validator.setDecimals(10)

        for enum_member in LocalRegistrationType:
            self.combo_box_icp.addItem(enum_member.name)

        # Max correspondence
        layout_correspondence = QHBoxLayout()
        correspondence_widget = QWidget()
        correspondence_widget.setLayout(layout_correspondence)
        correspondence_label = QLabel("Max correspondence: ")
        correspondence_label.setFixedWidth(150)
        self.correspondence_lineedit = QLineEdit("5.0")
        self.correspondence_lineedit.setFixedWidth(60)
        self.correspondence_lineedit.setValidator(double_validator)
        layout_correspondence.addWidget(correspondence_label)
        layout_correspondence.addWidget(self.correspondence_lineedit)
        layout_correspondence.addStretch()

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
        layout_fitness = QHBoxLayout()
        fitness_widget = QWidget()
        fitness_widget.setLayout(layout_fitness)
        fitness_label = QLabel("Relative fitness: ")
        fitness_label.setFixedWidth(100)
        self.fitness_lineedit = QLineEdit("0.000001")
        self.fitness_lineedit.setFixedWidth(60)
        self.fitness_lineedit.setValidator(double_validator)
        layout_fitness.addWidget(fitness_label)
        layout_fitness.addWidget(self.fitness_lineedit)
        layout_fitness.addStretch()

        # Relative RMSE
        layout_rmse = QHBoxLayout()
        rmse_widget = QWidget()
        rmse_widget.setLayout(layout_rmse)
        rmse_label = QLabel("Relative RMSE: ")
        rmse_label.setFixedWidth(100)
        self.rmse_lineedit = QLineEdit("0.000001")
        self.rmse_lineedit.setFixedWidth(60)
        self.rmse_lineedit.setValidator(double_validator)
        layout_rmse.addWidget(rmse_label)
        layout_rmse.addWidget(self.rmse_lineedit)
        layout_rmse.addStretch()

        # Max iterations
        layout_iteration = QHBoxLayout()
        iteration_widget = QWidget()
        iteration_widget.setLayout(layout_iteration)
        iteration_label = QLabel("Max iteration: ")
        iteration_label.setFixedWidth(100)
        self.iteration_lineedit = QLineEdit("30")
        self.iteration_lineedit.setFixedWidth(60)
        self.iteration_lineedit.setValidator(double_validator)
        layout_iteration.addWidget(iteration_label)
        layout_iteration.addWidget(self.iteration_lineedit)
        layout_iteration.addStretch()

        convergence_layout.addWidget(conv_label)
        convergence_layout.addWidget(fitness_widget)
        convergence_layout.addWidget(rmse_widget)
        convergence_layout.addWidget(iteration_widget)

        bt_apply = QPushButton("Start local registration")
        bt_apply.setStyleSheet("padding-left: 10px; padding-right: 10px;"
                               "padding-top: 2px; padding-bottom: 2px;")
        bt_apply.setFixedSize(250, 30)
        bt_apply.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        layout.addWidget(type_label)
        layout.addWidget(self.combo_box_icp)
        layout.addWidget(correspondence_widget)
        layout.addSpacing(5)
        layout.addWidget(convergence_widget)
        layout.addWidget(bt_apply)
        layout.addStretch()

        bt_apply.clicked.connect(self.registration_button_pressed)

    def registration_button_pressed(self):
        registration_type = LocalRegistrationType(self.combo_box_icp.currentIndex())
        max_correspondence = float(self.correspondence_lineedit.text())
        relative_fitness = float(self.fitness_lineedit.text())
        relative_rmse = float(self.rmse_lineedit.text())
        max_iteration = float(self.iteration_lineedit.text())
        self.signal_do_registration.emit(registration_type,
                                         max_correspondence, relative_fitness, relative_rmse, max_iteration)
