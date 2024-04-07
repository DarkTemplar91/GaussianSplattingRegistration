from PyQt5.QtCore import QLocale, pyqtSignal, Qt
from PyQt5.QtGui import QDoubleValidator, QIntValidator, QPalette
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QComboBox, QWidget, QCheckBox, QSizePolicy, \
    QScrollArea, QFrame, QPushButton, QStackedWidget, QHBoxLayout
from open3d.cpu.pybind.pipelines.registration import CorrespondenceCheckerBasedOnEdgeLength, \
    CorrespondenceCheckerBasedOnDistance, CorrespondenceCheckerBasedOnNormal

from src.gui.widgets.optional_value_widget import OptionalInputField
from src.gui.widgets.simple_input_field_widget import SimpleInputField
from src.utils.global_registration_util import GlobalRegistrationType, RANSACEstimationMethod
import src.utils.graphics_utils as graphic_util


class GlobalRegistrationTab(QWidget):
    signal_do_ransac = pyqtSignal(float, bool, float, RANSACEstimationMethod, int, list, int, float)
    signal_do_fgr = pyqtSignal(float, float, bool, bool, float, int, float, int, bool)

    def __init__(self):
        super().__init__()

        # Inputs for Fast Global Registration arguments
        self.checkbox_tuple_test = None
        self.max_tuple_count_widget = None
        self.tuple_scale_widget = None
        self.max_iterations_fgr_widget = None
        self.maximum_correspondence_fgr_widget = None
        self.checkbox_decrease_mu = None
        self.checkbox_use_absolute_scale = None
        self.division_factor_widget = None

        # Inputs for RANSAC arguments
        self.max_iterations_ransac_widget = None
        self.confidence_widget = None
        self.normal_checker = None
        self.distance_checker = None
        self.edge_length_checker = None
        self.ransac_iteration_widget = None
        self.combobox_estimation_method = None
        self.max_correspondence_ransac_widget = None
        self.checkbox_mutual = None

        registration_layout = QVBoxLayout()
        self.setLayout(registration_layout)

        scroll_widget = QScrollArea()
        scroll_widget.setBackgroundRole(QPalette.Background)
        scroll_widget.setFrameShadow(QFrame.Plain)
        scroll_widget.setFrameShape(QFrame.NoFrame)
        scroll_widget.setWidgetResizable(True)
        scroll_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        layout = QVBoxLayout()
        inner_widget = QWidget()
        inner_widget.setLayout(layout)
        scroll_widget.setWidget(inner_widget)

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
        self.stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        type_label = QLabel("Global registration type")
        self.combo_box_global = QComboBox()
        self.combo_box_global.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.combo_box_global.currentIndexChanged.connect(self.global_type_changed)

        for enum_member in GlobalRegistrationType:
            self.combo_box_global.addItem(enum_member.instance_name)

        # Voxel size for downsampling
        self.voxel_size_widget = SimpleInputField("Voxel size for downsampling:", "0.05",
                                                  validator=self.double_validator)

        # Stack for RANSAC
        self.ransac_widget = self.create_ransac_stack_widget()
        self.ransac_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # Stack for FGR
        self.fgr_widget = self.create_fgr_stack_widget()
        self.fgr_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.stack.addWidget(self.ransac_widget)
        self.stack.addWidget(self.fgr_widget)
        self.stack.setCurrentIndex(0)

        bt_apply = QPushButton("Start global registration")
        bt_apply.setStyleSheet(f"padding-left: 10px; padding-right: {int(graphic_util.SIZE_SCALE_X * 10)}px;"
                               f"padding-top: 2px; padding-bottom: {int(graphic_util.SIZE_SCALE_X * 2)}px;")
        bt_apply.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        bt_apply.setFixedHeight(int(30 * graphic_util.SIZE_SCALE_Y))
        bt_apply.clicked.connect(self.registration_button_pressed)

        layout.addWidget(type_label)
        layout.addWidget(self.combo_box_global)
        layout.addWidget(self.voxel_size_widget)
        layout.addWidget(self.stack, stretch=1)
        layout.addStretch()

        registration_layout.addWidget(scroll_widget)
        registration_layout.addWidget(bt_apply)

    def create_ransac_stack_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.checkbox_mutual = QCheckBox()
        self.checkbox_mutual.setText("Mutual filtering")
        self.checkbox_mutual.setStyleSheet(
            "QCheckBox::indicator {"
            f"    width: {int(graphic_util.SIZE_SCALE_X * 20)}px;"
            f"    height: {int(graphic_util.SIZE_SCALE_Y * 20)}px;"
            "}"
            "QCheckBox::indicator::text {"
            f"    padding-left: {int(graphic_util.SIZE_SCALE_X * 10)}px;"
            "}"
        )

        self.max_correspondence_ransac_widget = SimpleInputField("Maximum correspondence:", "5.0",
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
        estimation_layout.addStretch()

        self.ransac_iteration_widget = SimpleInputField("RANSAC iterations:", "3",
                                                        validator=self.int_validator)

        # Checkers
        checker_label = QLabel("Alignment checker")
        checker_label.setStyleSheet(
            "QLabel {"
            "    font-size: 11pt;"
            "    font-weight: bold;"
            f"    padding: {int(graphic_util.SIZE_SCALE_X * 8)}px;"
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
            "    font-size: 11pt;"
            "    font-weight: bold;"
            f"    padding: {int(graphic_util.SIZE_SCALE_X * 8)}px;"
            "}"
        )

        convergence_widget = QWidget()
        convergence_layout = QVBoxLayout()
        convergence_widget.setLayout(convergence_layout)
        self.confidence_widget = SimpleInputField("Confidence:", "0.999", 100, validator=self.double_validator)
        self.max_iterations_ransac_widget = SimpleInputField("Max iterations:", "100000", 100,
                                                             validator=self.int_validator)
        convergence_layout.addWidget(self.confidence_widget)
        convergence_layout.addWidget(self.max_iterations_ransac_widget)

        layout.addWidget(self.checkbox_mutual)
        layout.addWidget(self.max_correspondence_ransac_widget)
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

        widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Checkers
        options_label = QLabel("Options")
        options_label.setStyleSheet(
            "QLabel {"
            "    font-size: 11pt;"
            "    font-weight: bold;"
            f"    padding: {int(graphic_util.SIZE_SCALE_X * 8)}px;"
            "}"
        )

        layout.addWidget(options_label)
        widget_options = QWidget()
        layout_options = QVBoxLayout()
        widget_options.setLayout(layout_options)

        self.division_factor_widget = SimpleInputField("Division factor:", "1.4", validator=self.double_validator)
        self.checkbox_use_absolute_scale = QCheckBox()
        self.checkbox_use_absolute_scale.setText("Use absolute scale")
        self.checkbox_use_absolute_scale.setStyleSheet(
            "QCheckBox::indicator {"
            f"    width: {int(graphic_util.SIZE_SCALE_X * 20)}px;"
            f"    height: {int(graphic_util.SIZE_SCALE_Y * 20)}px;"
            "}"
            "QCheckBox::indicator::text {"
            f"    padding-left: {int(graphic_util.SIZE_SCALE_X * 10)}px;"
            "}"
        )
        self.checkbox_decrease_mu = QCheckBox()
        self.checkbox_decrease_mu.setText("Decrease mu")
        self.checkbox_decrease_mu.setStyleSheet(
            "QCheckBox::indicator {"
            f"    width: {int(graphic_util.SIZE_SCALE_X * 20)}px;"
            f"    height: {int(graphic_util.SIZE_SCALE_Y * 20)}px;"
            "}"
            "QCheckBox::indicator::text {"
            f"    padding-left: {int(graphic_util.SIZE_SCALE_X * 10)}px;"
            "}"
        )
        self.maximum_correspondence_fgr_widget = SimpleInputField("Maximum correspondence:",
                                                                  "0.025", validator=self.double_validator)
        self.max_iterations_fgr_widget = SimpleInputField("Iteration number: ",
                                                          "64", validator=self.int_validator)
        self.tuple_scale_widget = SimpleInputField("Tuple scale: ",
                                                   "0.95", validator=self.double_validator)
        self.max_tuple_count_widget = SimpleInputField("Max tuple count: ",
                                                       "1000", validator=self.int_validator)

        self.checkbox_tuple_test = QCheckBox()
        self.checkbox_tuple_test.setChecked(True)
        self.checkbox_tuple_test.setText("Tuple test")
        self.checkbox_tuple_test.setStyleSheet(
            "QCheckBox::indicator {"
            f"    width: {int(graphic_util.SIZE_SCALE_X * 20)}px;"
            f"    height: {int(graphic_util.SIZE_SCALE_Y * 20)}px;"
            "}"
            "QCheckBox::indicator::text {"
            f"    padding-left: {int(graphic_util.SIZE_SCALE_X * 10)}px;"
            "}"
        )

        layout_options.addWidget(self.division_factor_widget)
        layout_options.addWidget(self.checkbox_use_absolute_scale)
        layout_options.addWidget(self.checkbox_decrease_mu)
        layout_options.addWidget(self.maximum_correspondence_fgr_widget)
        layout_options.addWidget(self.max_iterations_fgr_widget)
        layout_options.addWidget(self.tuple_scale_widget)
        layout_options.addWidget(self.max_tuple_count_widget)
        layout_options.addWidget(self.checkbox_tuple_test)
        layout_options.addStretch()

        layout.addWidget(widget_options)
        layout.addStretch()

        return widget

    def global_type_changed(self, index):
        self.stack.setCurrentIndex(index)
        current_widget = self.stack.currentWidget()
        if current_widget is not None:
            height = current_widget.sizeHint().height()
            self.stack.setFixedHeight(int(height * graphic_util.SIZE_SCALE_Y))

    def registration_button_pressed(self):
        if self.combo_box_global.currentIndex() == 0:
            self.emit_ransac_signal()
            return

        self.emit_fgr_signal()

    def emit_ransac_signal(self):
        voxel_size = float(self.voxel_size_widget.lineedit.text())
        mutual_filter = self.checkbox_mutual.isChecked()
        max_correspondence = float(self.max_correspondence_ransac_widget.lineedit.text())
        estimation_method = RANSACEstimationMethod(self.combobox_estimation_method.currentIndex())
        ransac_n = int(self.ransac_iteration_widget.lineedit.text())
        checkers = self.get_ransac_checkers_list()
        max_iteration = int(self.max_iterations_ransac_widget.lineedit.text())
        confidence = float(self.confidence_widget.lineedit.text())
        self.signal_do_ransac.emit(voxel_size, mutual_filter, max_correspondence, estimation_method,
                                   ransac_n, checkers, max_iteration, confidence)

    def emit_fgr_signal(self):
        voxel_size = float(self.voxel_size_widget.lineedit.text())
        division_factor = float(self.division_factor_widget.lineedit.text())
        use_absolute_scale = self.checkbox_use_absolute_scale.isChecked()
        decrease_mu = self.checkbox_decrease_mu.isChecked()
        maximum_correspondence = float(self.maximum_correspondence_fgr_widget.lineedit.text())
        max_iterations = int(self.max_iterations_fgr_widget.lineedit.text())
        tuple_scale = float(self.tuple_scale_widget.lineedit.text())
        max_tuple_count = int(self.max_tuple_count_widget.lineedit.text())
        tuple_test = self.checkbox_tuple_test.isChecked()

        self.signal_do_fgr.emit(voxel_size, division_factor, use_absolute_scale, decrease_mu, maximum_correspondence,
                                max_iterations, tuple_scale, max_tuple_count, tuple_test)

    def get_ransac_checkers_list(self):
        checkers = []
        if self.distance_checker.is_checked():
            checkers.append(CorrespondenceCheckerBasedOnDistance(float(self.distance_checker.get_value())))
        if self.edge_length_checker.is_checked():
            checkers.append(CorrespondenceCheckerBasedOnEdgeLength(float(self.edge_length_checker.get_value())))
        if self.normal_checker.is_checked():
            checkers.append(CorrespondenceCheckerBasedOnNormal(float(self.normal_checker.get_value())))
        return checkers
