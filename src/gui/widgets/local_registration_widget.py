from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit, QSizePolicy, \
    QGroupBox, QComboBox


class LocalRegistrationGroup(QGroupBox):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.setTitle("Local registration")

        type_label = QLabel("Local registration type")
        combo_box_icp = QComboBox()
        # TODO: Use enums
        combo_box_icp.addItems(["Point-to-Point ICP", "Point-to-Plane ICP", "Color ICP", "General ICP"])

        # Max correspondence
        layout_correspondence = QHBoxLayout()
        correspondence_widget = QWidget()
        correspondence_widget.setLayout(layout_correspondence)
        correspondence_label = QLabel("Max correspondence: ")
        correspondence_label.setFixedWidth(150)
        correspondence_lineedit = QLineEdit("0.0")
        correspondence_lineedit.setFixedWidth(60)
        layout_correspondence.addWidget(correspondence_label)
        layout_correspondence.addWidget(correspondence_lineedit)
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
        fitness_lineedit = QLineEdit("0.000001")
        fitness_lineedit.setFixedWidth(60)
        layout_fitness.addWidget(fitness_label)
        layout_fitness.addWidget(fitness_lineedit)
        layout_fitness.addStretch()

        # Relative RMSE
        layout_rmse = QHBoxLayout()
        rmse_widget = QWidget()
        rmse_widget.setLayout(layout_rmse)
        rmse_label = QLabel("Relative RMSE: ")
        rmse_label.setFixedWidth(100)
        rmse_lineedit = QLineEdit("0.000001")
        rmse_lineedit.setFixedWidth(60)
        layout_rmse.addWidget(rmse_label)
        layout_rmse.addWidget(rmse_lineedit)
        layout_rmse.addStretch()

        # Max iterations
        layout_iteration = QHBoxLayout()
        iteration_widget = QWidget()
        iteration_widget.setLayout(layout_iteration)
        iteration_label = QLabel("Max iteration: ")
        iteration_label.setFixedWidth(100)
        iteration_lineedit = QLineEdit("30")
        iteration_lineedit.setFixedWidth(60)
        layout_iteration.addWidget(iteration_label)
        layout_iteration.addWidget(iteration_lineedit)
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
        layout.addWidget(combo_box_icp)
        layout.addWidget(correspondence_widget)
        layout.addSpacing(5)
        layout.addWidget(convergence_widget)
        layout.addWidget(bt_apply)
        layout.addStretch()
