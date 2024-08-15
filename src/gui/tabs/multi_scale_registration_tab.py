from PyQt5 import QtCore
from PyQt5.QtCore import QLocale, QRegularExpression
from PyQt5.QtGui import QDoubleValidator, QRegularExpressionValidator, QPalette
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QComboBox, QCheckBox, QSizePolicy, QPushButton, QHBoxLayout, \
    QFrame, QScrollArea, QStackedWidget

from src.gui.widgets.file_selector_widget import FileSelector
from src.gui.widgets.simple_input_field_widget import SimpleInputField

from src.utils.local_registration_util import LocalRegistrationType, KernelLossFunctionType
import src.utils.graphics_utils as graphic_util


class MultiScaleRegistrationTab(QWidget):
    signal_do_registration = QtCore.pyqtSignal(bool, str, str, LocalRegistrationType, float, float,
                                               list, list,
                                               KernelLossFunctionType, float, bool)

    def __init__(self, input_path):
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
            "    font-size: 11pt;"
            "    font-weight: bold;"
            f"    padding: {int(graphic_util.SIZE_SCALE_X * 8)}px;"
            "}"
        )

        self.sparse_checkbox = QCheckBox()
        self.sparse_checkbox.setText("Use sparse point clouds for initial registration")
        self.sparse_checkbox.setStyleSheet(
            "QCheckBox::indicator {"
            f"    width: {int(graphic_util.SIZE_SCALE_X * 20)}px;"
            f"    height: {int(graphic_util.SIZE_SCALE_Y * 20)}px;"
            "}"
            "QCheckBox::indicator::text {"
            f"    padding-left: {int(graphic_util.SIZE_SCALE_X * 10)}px;"
            "}"
        )
        self.sparse_checkbox.stateChanged.connect(self.checkbox_changed)

        # File selectors for sparse input
        self.fs_sparse1 = FileSelector(text="First sparse input:", base_path=input_path)
        self.fs_sparse2 = FileSelector(text="Second sparse input:", base_path=input_path)
        self.fs_sparse1.setEnabled(False)
        self.fs_sparse2.setEnabled(False)

        # Local registration type
        registration_type_label = QLabel("Local registration type")
        self.combo_box_icp = QComboBox()
        self.combo_box_icp.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        for enum_member in LocalRegistrationType:
            self.combo_box_icp.addItem(enum_member.instance_name)

        # Basic input fields
        self.fitness_widget = SimpleInputField("Relative fitness:", "0.000001", 100, 60,
                                               double_validator)
        self.rmse_widget = SimpleInputField("Relative RMSE:", "0.000001", 100, 60,
                                            double_validator)
        self.iter_values = SimpleInputField("Iteration values:", "50,30,20", 100, 150, int_list_validator)

        downscale_type_label = QLabel("Downscale type: ")
        downscale_type_label.setFixedWidth(100)
        self.combo_box_multiscale = QComboBox()
        self.combo_box_multiscale.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.combo_box_multiscale.addItem("Voxel downsampling")
        self.combo_box_multiscale.addItem("HEM Gaussian mixture")
        self.combo_box_multiscale.currentIndexChanged.connect(self.downscale_type_changed)

        downscale_type_widget = QWidget()
        downscale_type_layout = QHBoxLayout()
        downscale_type_widget.setLayout(downscale_type_layout)
        downscale_type_layout.addWidget(downscale_type_label)
        downscale_type_layout.addWidget(self.combo_box_multiscale)
        downscale_type_layout.addStretch()

        # Only, when using voxel downsample
        self.voxel_values = SimpleInputField("Voxel values:", "5,2.5,2", 100, 150, double_list_validator)

        # Outlier rejection
        outlier_layout = QVBoxLayout()
        outlier_widget = QWidget()
        outlier_widget.setLayout(outlier_layout)

        rejection_label = QLabel("Robust Kernel outlier rejection")
        rejection_label.setStyleSheet(
            "QLabel {"
            "    font-size: 11pt;"
            "    font-weight: bold;"
            f"    padding: {int(graphic_util.SIZE_SCALE_X * 8)}px;"
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

        bt_apply = QPushButton("Start multi-scale registration")
        bt_apply.setStyleSheet(f"padding-left: 10px; padding-right: {int(graphic_util.SIZE_SCALE_X * 10)}px;"
                               f"padding-top: 2px; padding-bottom: {int(graphic_util.SIZE_SCALE_X * 2)}px;")
        bt_apply.setFixedHeight(int(30 * graphic_util.SIZE_SCALE_Y))
        bt_apply.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        bt_apply.clicked.connect(self.registration_button_pressed)

        layout.addWidget(label_title)
        layout.addWidget(self.sparse_checkbox)
        layout.addWidget(self.fs_sparse1)
        layout.addWidget(self.fs_sparse2)
        layout.addWidget(registration_type_label)
        layout.addWidget(self.combo_box_icp)

        layout.addWidget(self.fitness_widget)
        layout.addWidget(self.rmse_widget)
        layout.addWidget(self.iter_values)

        layout.addWidget(downscale_type_widget)
        layout.addWidget(self.voxel_values)

        layout.addWidget(rejection_label)
        layout.addWidget(outlier_widget)
        layout.addStretch()

        registration_layout.addWidget(scroll_widget)
        registration_layout.addWidget(bt_apply)

    def checkbox_changed(self, state):
        self.fs_sparse1.setEnabled(state)
        self.fs_sparse2.setEnabled(state)

        if state:
            return

        self.fs_sparse1.inputField.setText("")
        self.fs_sparse1.file_path = ""

        self.fs_sparse2.inputField.setText("")
        self.fs_sparse2.file_path = ""

    def registration_button_pressed(self):
        use_corresponding = self.sparse_checkbox.isChecked()
        sparse_first = self.fs_sparse1.file_path
        sparse_second = self.fs_sparse2.file_path
        registration_type = LocalRegistrationType(self.combo_box_icp.currentIndex())
        relative_fitness = float(self.fitness_widget.lineedit.text())
        relative_rmse = float(self.rmse_widget.lineedit.text())

        voxel_values = list(map(float, filter(None, self.voxel_values.lineedit.text().split(","))))
        iter_values = list(map(int, filter(None, self.iter_values.lineedit.text().split(","))))

        rejection_type = KernelLossFunctionType(self.combo_box_outlier.currentIndex())
        k_value = float(self.k_value_widget.lineedit.text())
        use_mixture = self.combo_box_multiscale.currentIndex() == 1

        self.signal_do_registration.emit(use_corresponding, sparse_first, sparse_second,
                                         registration_type,
                                         relative_fitness, relative_rmse,
                                         voxel_values, iter_values,
                                         rejection_type, k_value, use_mixture)

    def rejection_type_changed(self, index):
        self.k_value_widget.setEnabled(index != 0)

    def downscale_type_changed(self, index):
        self.voxel_values.label.setText("Voxel values:" if index == 0 else "Correspondences:")
        self.voxel_values.update()
