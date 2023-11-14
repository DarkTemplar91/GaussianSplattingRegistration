import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QLocale
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, \
    QTableWidget, QGridLayout, QLineEdit, QPushButton, QSizePolicy


class Transformation3DPicker(QWidget):
    class MatrixCell(QLineEdit):
        cell_number = 0

        value_changed = QtCore.pyqtSignal(int, int, float)

        def __init__(self, value=0.0):
            super().__init__()

            locale = QLocale(QLocale.English)
            double_validator = QDoubleValidator()
            double_validator.setLocale(locale)
            double_validator.setRange(-9999.0, 9999.0)
            double_validator.setDecimals(10)

            self.row = int(Transformation3DPicker.MatrixCell.cell_number / 4)
            self.col = self.cell_number % 4
            Transformation3DPicker.MatrixCell.cell_number += 1

            self.setFixedSize(50, 50)
            self.setAlignment(Qt.AlignLeft)
            self.value = value
            self.setText(str(self.value))
            self.setValidator(double_validator)
            self.textEdited.connect(self.update_cell_value)

        def update_cell_value(self, text):
            try:
                self.value = float(text)
                self.value_changed.emit(self.row, self.col, self.value)
            except ValueError:
                pass

    transformation_matrix_changed = QtCore.pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

        label = QLabel("Transformation matrix")
        label.setStyleSheet(
            "QLabel {"
            "    font-size: 14px;"
            "    font-weight: bold;"  # Bold font
            "    padding: 8px;"  # Padding
            "}"
        )

        self.matrix_table = QTableWidget()
        self.matrix_table.setRowCount(4)
        self.matrix_table.setColumnCount(4)

        self.matrix_widget = QWidget()
        grid_layout = QGridLayout()
        self.matrix_widget.setLayout(grid_layout)

        self.cells = []
        self.transformation_matrix = np.array([[1, 0, 0, 0],
                                               [0, 1, 0, 0],
                                               [0, 0, 1, 0],
                                               [0, 0, 0, 1]], dtype=float)

        for iRow in range(4):
            for iCol in range(4):
                cell = self.MatrixCell(self.transformation_matrix[iRow, iCol])
                grid_layout.addWidget(cell, iRow, iCol)
                self.cells.append(cell)

        for cell in self.cells:
            cell.value_changed.connect(self.transformation_changed)

        button_reset = QPushButton("Reset transformation matrix")
        button_reset.setStyleSheet("padding-left: 10px; padding-right: 10px;"
                                   "padding-top: 2px; padding-bottom: 2px;")
        button_reset.setFixedSize(250, 30)
        button_reset.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        button_reset.clicked.connect(self.reset_transformation)

        layout.addWidget(label)
        layout.addWidget(self.matrix_widget)
        layout.addWidget(button_reset, alignment=Qt.AlignCenter)

    def transformation_changed(self, row, col, value):
        self.transformation_matrix[row, col] = value
        self.transformation_matrix_changed.emit(self.transformation_matrix)

    def set_transformation(self, transformation_matrix):
        for cell in self.cells:
            self.transformation_matrix[cell.row][cell.col] = transformation_matrix[cell.row][cell.col]
            value = transformation_matrix[cell.row][cell.col]
            cell.setText(str(value))
            cell.setCursorPosition(0)

        self.transformation_matrix_changed.emit(self.transformation_matrix)

    def reset_transformation(self):
        self.set_transformation(np.eye(4))
