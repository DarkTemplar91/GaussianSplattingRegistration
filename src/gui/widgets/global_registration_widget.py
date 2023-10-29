from PyQt5.QtCore import QLocale, pyqtSignal
from PyQt5.QtGui import QDoubleValidator, QIntValidator, QPalette
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QComboBox, QWidget, QCheckBox, QSizePolicy, \
    QScrollArea, QFrame, QPushButton, QStackedWidget, QHBoxLayout
from open3d.cpu.pybind.pipelines.registration import CorrespondenceCheckerBasedOnEdgeLength, \
    CorrespondenceCheckerBasedOnDistance, CorrespondenceCheckerBasedOnNormal

from src.gui.widgets.optional_value_widget import OptionalInputField
from src.gui.widgets.registration_input_field_widget import RegistrationInputField
from src.utils.global_registration_util import GlobalRegistrationType, RANSACEstimationMethod


# TODO: Finish
class GlobalRegistrationTab(QScrollArea):
    signal_do_ransac = pyqtSignal(float, bool, float, RANSACEstimationMethod, int, list, int, float)

    def __init__(self):
        super().__init__()

        # Inputs for RANSAC arguments
        self.max_iterations_widget = None
        self.confidence_widget = None
        self.normal_checker = None
        self.distance_checker = None
        self.edge_length_checker = None
        self.ransac_iteration_widget = None
        self.combobox_estimation_method = None
        self.max_correspondence_widget = None
        self.checkbox_mutual = None

        widget = QWidget()
        self.setWidget(widget)
        layout = QVBoxLayout()
        widget.setLayout(layout)

        self.setBackgroundRole(QPalette.Background)
        self.setFrameShadow(QFrame.Plain)
        self.setFrameShape(QFrame.NoFrame)
        self.setWidgetResizable(True)

        locale = QLocale(QLocale.English)
        self.double_validator = QDoubleValidator()
        self.double_validator.setLocale(locale)
        self.double_validator.setRange(0.0, 9999.0)
        self.double_validator.setDecimals(10)

        self.int_validator = QIntValidator()
        self.int_validator.setLocale(locale)
        self.int_validator.setRange(0, 999999999)

        # Stack for switching between RANSAC and FGR
        self.stack = QStackedWidget()

        type_label = QLabel("Global registration type")
        self.combo_box_global = QComboBox()
        self.combo_box_global.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.combo_box_global.currentIndexChanged.connect(self.global_type_changed)

        for enum_member in GlobalRegistrationType:
            self.combo_box_global.addItem(enum_member.instance_name)

        # Voxel size for downsampling
        self.voxel_size_widget = RegistrationInputField("Voxel size for downsampling:", "5.0",
                                                        validator=self.double_validator)

        # Stack for RANSAC
        ransac_widget = self.create_ransac_stack_widget()
        # Stack for FGR
        fgr_widget = self.create_fgr_stack_widget()

        self.stack.addWidget(ransac_widget)
        self.stack.addWidget(fgr_widget)
        self.stack.setCurrentIndex(0)

        bt_apply = QPushButton("Start global registration")
        bt_apply.setStyleSheet("padding-left: 10px; padding-right: 10px;"
                               "padding-top: 2px; padding-bottom: 2px;")
        bt_apply.setFixedSize(250, 30)
        bt_apply.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        bt_apply.clicked.connect(self.registration_button_pressed)

        layout.addWidget(type_label)
        layout.addWidget(self.combo_box_global)
        layout.addWidget(self.voxel_size_widget)
        layout.addWidget(self.stack)
        layout.addWidget(bt_apply)
        layout.addStretch()

    def create_ransac_stack_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        self.checkbox_mutual = QCheckBox()
        self.checkbox_mutual.setText("Mutual filtering")
        self.checkbox_mutual.setStyleSheet(
            "QCheckBox::indicator {"
            "    width: 20px;"
            "    height: 20px;"
            "}"
            "QCheckBox::indicator::text {"
            "    padding-left: 10px;"
            "}"
        )

        self.max_correspondence_widget = RegistrationInputField("Maximum correspondence:", "5.0",
                                                                validator=self.double_validator)

        type_label = QLabel("Estimation type: ")
        self.combobox_estimation_method = QComboBox()
        self.combobox_estimation_method.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        for enum_member in RANSACEstimationMethod:
            self.combobox_estimation_method.addItem(enum_member.instance_name)

        estimation_widget = QWidget()
        estimation_layout = QHBoxLayout()
        estimation_widget.setLayout(estimation_layout)
        estimation_layout.addWidget(type_label)
        estimation_layout.addWidget(self.combobox_estimation_method)

        self.ransac_iteration_widget = RegistrationInputField("RANSAC iterations:", "3",
                                                              validator=self.int_validator)

        # Checkers
        checker_label = QLabel("Alignment checker")
        checker_label.setStyleSheet(
            "QLabel {"
            "    font-size: 12px;"
            "    font-weight: bold;"
            "    padding: 8px;"
            "}"
        )
        self.edge_length_checker = OptionalInputField("Edge Length:", "0.0", 75, validator=self.double_validator)
        self.distance_checker = OptionalInputField("Distance:", "0.0", 75, validator=self.double_validator)
        self.normal_checker = OptionalInputField("Normal:", "0.0", 75, validator=self.double_validator)

        checker_widget = QWidget()
        checker_layout = QVBoxLayout()
        checker_widget.setLayout(checker_layout)
        checker_layout.addWidget(self.edge_length_checker)
        checker_layout.addWidget(self.distance_checker)
        checker_layout.addWidget(self.normal_checker)

        # Convergence criteria
        convergence_label = QLabel("Convergence criteria")
        convergence_label.setStyleSheet(
            "QLabel {"
            "    font-size: 12px;"
            "    font-weight: bold;"
            "    padding: 8px;"
            "}"
        )

        convergence_widget = QWidget()
        convergence_layout = QVBoxLayout()
        convergence_widget.setLayout(convergence_layout)
        self.confidence_widget = RegistrationInputField("Confidence:", "0.999", 100, validator=self.double_validator)
        self.max_iterations_widget = RegistrationInputField("Max iterations:", "100000", 100, validator=self.int_validator)
        convergence_layout.addWidget(self.confidence_widget)
        convergence_layout.addWidget(self.max_iterations_widget)

        layout.addWidget(self.checkbox_mutual)
        layout.addWidget(self.max_correspondence_widget)
        layout.addWidget(estimation_widget)
        layout.addWidget(self.ransac_iteration_widget)
        layout.addWidget(checker_label)
        layout.addWidget(checker_widget)
        layout.addWidget(convergence_label)
        layout.addWidget(convergence_widget)

        return widget

    def create_fgr_stack_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        return widget

    def global_type_changed(self, index):
        self.stack.setCurrentIndex(index)

    def registration_button_pressed(self):
        if self.combo_box_global.currentIndex() == 0:
            self.emit_ransac_signal()
            return

        self.emit_fgr_signal()

    def emit_ransac_signal(self):
        voxel_size = float(self.voxel_size_widget.lineedit.text())
        mutual_filter = self.checkbox_mutual.isChecked()
        max_correspondence = float(self.max_correspondence_widget.lineedit.text())
        estimation_method = RANSACEstimationMethod(self.combobox_estimation_method.currentIndex())
        ransac_n = int(self.ransac_iteration_widget.lineedit.text())
        checkers = self.get_ransac_checkers_list()
        max_iteration = int(self.max_iterations_widget.lineedit.text())
        confidence = float(self.confidence_widget.lineedit.text())
        self.signal_do_ransac.emit(voxel_size, mutual_filter, max_correspondence, estimation_method,
                                   ransac_n, checkers, max_iteration, confidence)

    def get_ransac_checkers_list(self):
        checkers = []
        if self.distance_checker.is_checked():
            checkers.append(CorrespondenceCheckerBasedOnDistance(float(self.distance_checker.get_value())))
        if self.edge_length_checker.is_checked():
            checkers.append(CorrespondenceCheckerBasedOnEdgeLength(float(self.edge_length_checker.get_value())))
        if self.normal_checker.is_checked():
            checkers.append(CorrespondenceCheckerBasedOnNormal(float(self.normal_checker.get_value())))
        return checkers
